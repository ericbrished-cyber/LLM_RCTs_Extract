import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Dict

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from utils import (
    get_xml,
    get_fulltext,
    list_pmcids,
    get_icos,
    get_prompt_all,
    get_prompt_guided,
)
from spinner import Spinner
from XML_from_PMC import download_pmc_xml
from batch_evaluation import BatchEvaluator

# ---------------------- Setup ---------------------- #

load_dotenv(find_dotenv())

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

pdf_folder = "data/PDF_test"
markdown_folder = "data/Markdown"
xml_folder = "data/XML_fulltext"
base_output_folder = "./outputs"
eval_folder = "./evaluation_results"

os.makedirs(base_output_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(markdown_folder, exist_ok=True)
os.makedirs(xml_folder, exist_ok=True)
os.makedirs(eval_folder, exist_ok=True)


# ---------------------- GPT-5 helpers ---------------------- #

def run_gpt5_extraction_pdf(
    pdf_path: str,
    prompt: str,
    model_name: str = "gpt-5.1-mini",
) -> dict:
    """
    GPT-5 extraction using the PDF directly via input_file.

    Returns: {"extractions": [...]}
    """
    with open(pdf_path, "rb") as f:
        file_obj = client.files.create(
            file=f,
            purpose="user_data",
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an information extraction model that reads the attached PDF "
                'and outputs ONLY valid JSON of the form {"extractions":[ ... ]}.'
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_file", "file_id": file_obj.id},
            ],
        },
    ]

    resp = client.responses.create(
        model=model_name,
        input=messages,
    )

    # --- Find the first output item that actually has content ---
    output = getattr(resp, "output", None)
    if not output:
        raise ValueError(f"Model returned no output: {resp}")

    message_item = None
    for item in output:
        content = getattr(item, "content", None)
        if content:
            message_item = item
            break

    if message_item is None:
        raise ValueError(f"Model returned no message content: {resp}")

    content_list = message_item.content
    if not content_list:
        raise ValueError(f"Message has empty content: {resp}")

    text_chunk = None
    for chunk in content_list:
        if hasattr(chunk, "text") and chunk.text is not None:
            text_chunk = chunk
            break

    if text_chunk is None:
        raise ValueError(f"Message content has no text chunk: {resp}")

    raw_json = text_chunk.text

    data = json.loads(raw_json)

    # OPTIONAL: map 'value' → 'extraction_text'
    if "extractions" in data and isinstance(data["extractions"], list):
        for ex in data["extractions"]:
            if "value" in ex and "extraction_text" not in ex:
                ex["extraction_text"] = str(ex["value"])

    if "extractions" not in data or not isinstance(data["extractions"], list):
        raise ValueError("GPT-5 response did not contain an 'extractions' list")

    return data




# ---------------------- Main runner ---------------------- #

def run_gpt5_with_eval(
    model: str = "gpt-5-mini",
    extraction_mode: str = "guided",  # "all" or "guided"
    run_evaluation: bool = True,
    run_name: Optional[str] = None,
):
    """
    Run GPT-5 extraction on PMC articles with optional batch evaluation.

    - For source_type="pdf": pass the PDF directly to GPT-5 via input_file.
    - For source_type="xml": pass plain text from XML.
    - Outputs:
        ./outputs/<run_name>/<PMCID>_<extraction_mode>_<source_type>.jsonl
      Each file has one line: {"pmcid": ..., "extractions": [...]}
    """
    pmcid_lst = list_pmcids(pdf_folder)
    total = len(pmcid_lst)

    # Generate run name if not provided
    if run_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{model}_{extraction_mode}_{timestamp}"

    # Create run-specific output folder
    run_output_folder = os.path.join(base_output_folder, run_name)
    os.makedirs(run_output_folder, exist_ok=True)

    suffix = f"_{extraction_mode}"

    print("=" * 80)
    print(f"GPT-5 EXTRACTION RUN: {run_name}")
    print("=" * 80)
    print(f"Model: {model}")
    print(f"Mode: {extraction_mode}")
    print(f"Articles: {total}")
    print(f"Output folder: {os.path.abspath(run_output_folder)}")
    print(f"Run evaluation: {run_evaluation}")
    print("=" * 80)
    print()

    stats = {
        "total": total,
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
    }
    failed_pmcids: List[Tuple[int, str]] = []

    # ------------- Loop over PMCIDs ------------- #
    for i, pmcid in enumerate(pmcid_lst, 1):
        # ===== STEP 1: Prepare input (PDF) =====
        try:
                # We will pass the PDF directly to GPT-5 (no markdown)
                pdf_path = os.path.join(pdf_folder, f"{pmcid}.pdf")

                if not os.path.exists(pdf_path):
                    print(
                        f"[{i}/{total}] PMCID={pmcid} ✗ PDF not found",
                        flush=True,
                    )
                    stats["failed"] += 1
                    failed_pmcids.append((pmcid, "PDF not found"))
                    continue

        except Exception as e:
            print(
                f"[{i}/{total}] PMCID={pmcid} ✗ failed to prepare input: {e}",
                flush=True,
            )
            stats["failed"] += 1
            failed_pmcids.append((pmcid, f"Input preparation: {e}"))
            continue

        # ===== STEP 2: Prepare prompt =====
        if extraction_mode == "all":
            prompt = get_prompt_all()
            mode_label = "all stats"

        elif extraction_mode == "guided":
            icos = get_icos(pmcid)
            if not icos:
                print(
                    f"[{i}/{total}] PMCID={pmcid} ⚠ no ICOs in annotations, skipping",
                    flush=True,
                )
                stats["skipped"] += 1
                continue

            prompt = get_prompt_guided(pmcid)
            mode_label = f"guided ({len(icos)} ICOs)"

        else:
            raise ValueError(
                f"Invalid extraction_mode: {extraction_mode}. Use 'all' or 'guided'"
            )

        # ===== STEP 3: Run GPT-5 extraction (PDF) =====
        label = f"[{i}/{total}] PMCID={pmcid} ({mode_label}) extracting…"

        try:
            max_attempts = 3
            extraction_successful = False
            result: Dict[str, any] = {}

            for attempt in range(1, max_attempts + 1):
                try:
                    with Spinner(label):
                            result = run_gpt5_extraction_pdf(
                                pdf_path=pdf_path,
                                prompt=prompt,
                                model_name=model,
                            )
                    extraction_successful = True
                    break

                except Exception as e:
                    msg = str(e)
                    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                        wait = 60 * attempt
                        print(
                            f"[{i}/{total}] PMCID={pmcid} quota error "
                            f"(attempt {attempt}/{max_attempts}), waiting {wait}s…",
                            flush=True,
                        )
                        time.sleep(wait)
                        continue
                    else:
                        raise

            if not extraction_successful:
                print(
                    f"[{i}/{total}] PMCID={pmcid} ✗ failed after {max_attempts} attempts (quota)",
                    flush=True,
                )
                stats["failed"] += 1
                failed_pmcids.append((pmcid, "Quota exhausted"))
                continue

            print(
                f"[{i}/{total}] PMCID={pmcid} ✓ extracted. Saving…",
                flush=True,
            )

            output_name = f"{pmcid}{suffix}.jsonl"
            jsonl_path = os.path.join(run_output_folder, output_name)

            # Save in the SAME JSONL format your evaluation expects
            out_doc = {
                "pmcid": pmcid,
                "extractions": result.get("extractions", []),
            }
            with open(jsonl_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(out_doc) + "\n")

            print(
                f"[{i}/{total}] PMCID={pmcid} ✓ saved {output_name}",
                flush=True,
            )

            stats["processed"] += 1
            stats["successful"] += 1

        except KeyboardInterrupt:
            print(
                f"\n[{i}/{total}] PMCID={pmcid} ✗ interrupted by user.",
                flush=True,
            )
            raise
        except Exception as e:
            print(
                f"\n[{i}/{total}] PMCID={pmcid} ✗ failed: {e}",
                flush=True,
            )
            stats["failed"] += 1
            failed_pmcids.append((pmcid, str(e)))
            continue

    # ===== SUMMARY =====
    print("\n" + "=" * 80)
    print("GPT-5 EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Total articles: {stats['total']}")
    print(f"Successfully processed: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (no ICOs): {stats['skipped']}")

    if failed_pmcids:
        print("\nFailed PMCIDs:")
        for pmcid, reason in failed_pmcids:
            print(f"  PMCID={pmcid}: {reason}")

    print("=" * 80)

    # ===== EVALUATION =====
    if run_evaluation and stats["successful"] > 0:
        print("\n" + "=" * 80)
        print("RUNNING EVALUATION (GPT-5)")
        print("=" * 80)

        try:
            evaluator = BatchEvaluator(
                gold_path="gold-standard/annotated_rct_dataset.json",
                output_dir=eval_folder,
            )

            results = evaluator.evaluate_directory(
                predictions_dir=run_output_folder,
                suffix_filter=suffix,   # matches "<pmcid><suffix>.jsonl"
                run_name=run_name,
            )
            return results

        except Exception as e:
            print(f"✗ Evaluation failed: {e}")
            return None

    elif run_evaluation and stats["successful"] == 0:
        print("\n⚠ Skipping evaluation - no successful extractions")
        return None

    return None


def main():
    """
    Example: GPT-5 guided extraction directly from PDFs, with evaluation.
    """
    run_gpt5_with_eval(
        model="gpt-5-mini",
        extraction_mode="guided", # or "all"
        run_evaluation=True,
        run_name="gpt5_direct_pdf_guided",
    )


if __name__ == "__main__":
    main()
