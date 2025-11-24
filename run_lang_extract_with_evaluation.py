import time
import os
from pathlib import Path
from datetime import datetime

from utils import (
    get_fulltext, 
    list_pmcids, 
    get_icos, 
    get_prompt_all, 
    get_prompt_guided,
    get_fewshotexamples, 
    visualize
)

from spinner import Spinner
from pdf_converter import convert_pdf_to_markdown
from batch_evaluation import BatchEvaluator

try:
    import langextract as lx
except Exception:
    lx = None

from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv())

# Directory setup
pdf_folder = "data/PDF_test"
markdown_folder = "data/Markdown"
base_output_folder = "./outputs"

os.makedirs(base_output_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(markdown_folder, exist_ok=True)
    

def run_lang_extract_with_eval(
    model="gemini-2.5-flash",
    extraction_mode="all",  # "all" or "guided"
    run_evaluation=True,
    run_name=None,
):
    """
    Run extraction task on PMC articles with optional batch evaluation.

    Args:
        model (str): Model identifier for langextract
        extraction_mode (str):
            - "all": Extract all statistical information (no ICO guidance)
            - "guided": Extract specific ICOs given in annotations
        run_evaluation (bool): Whether to run evaluation after extraction
        run_name (str): Name for this run (used in evaluation results)
    """
    pmcid_lst = list_pmcids(pdf_folder)
    total = len(pmcid_lst)
    
    if lx is None:
        raise ImportError(
            "Missing dependency: 'langextract' is not installed. "
            "Install project dependencies with: python -m pip install -r requirements.txt"
        )
    
    # Generate run name if not provided
    if run_name is None:
        # Sanitize model name for folder
        model_clean = model.replace("-", "_").replace(".", "_")
        run_name = f"LangExtract_{model_clean}_{extraction_mode}"
    
    # Create run-specific folders with new structure
    run_output_folder = os.path.join(base_output_folder, run_name)
    extractions_folder = os.path.join(run_output_folder, "extractions")
    visualizations_folder = os.path.join(run_output_folder, "visualizations")
    evaluation_folder = os.path.join(run_output_folder, "evaluation")
    
    os.makedirs(run_output_folder, exist_ok=True)
    os.makedirs(extractions_folder, exist_ok=True)
    os.makedirs(visualizations_folder, exist_ok=True)
    os.makedirs(evaluation_folder, exist_ok=True)
    
    # Suffix for output files
    suffix = f"_{extraction_mode}"
    
    print("=" * 80)
    print(f"LANGEXTRACT RUN: {run_name}")
    print("=" * 80)
    print(f"Model: {model}")
    print(f"Mode: {extraction_mode}")
    print(f"Articles: {total}")
    print(f"Output folder: {os.path.abspath(run_output_folder)}")
    print(f"  - Extractions: {os.path.abspath(extractions_folder)}")
    print(f"  - Visualizations: {os.path.abspath(visualizations_folder)}")
    print(f"  - Evaluation: {os.path.abspath(evaluation_folder)}")
    print(f"Run evaluation: {run_evaluation}")
    print("=" * 80)
    print()

    # Track statistics
    stats = {
        "total": total,
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
    }
    failed_pmcids = []
    
    for i, pmcid in enumerate(pmcid_lst, 1):
        # ===== STEP 1: Prepare input text =====
        try:
            pdf_path = os.path.join(pdf_folder, f"{pmcid}.pdf")
            if not os.path.exists(pdf_path):
                pdf_path = os.path.join(pdf_folder, f"PMCID{pmcid}.pdf")

                if not os.path.exists(pdf_path):
                    print(
                        f"[{i}/{total}] PMCID={pmcid} ✗ PDF not found",
                        flush=True,
                    )
                    stats["failed"] += 1
                    failed_pmcids.append((pmcid, "PDF not found"))
                    continue

            md_path = os.path.join(markdown_folder, f"{pmcid}.md")
            if not os.path.exists(md_path):
                print(
                    f"[{i}/{total}] PMCID={pmcid} - Converting PDF to Markdown.",
                    flush=True,
                )
                convert_pdf_to_markdown(pdf_path, output_dir=markdown_folder)

            input_text = get_fulltext(pmcid, text_folder_path=markdown_folder)
            if input_text.startswith("Markdown file for PMCID"):
                print(
                    f"[{i}/{total}] PMCID={pmcid} ✗ markdown conversion failed",
                    flush=True,
                )
                stats["failed"] += 1
                failed_pmcids.append((pmcid, "Markdown conversion failed"))
                continue

        except Exception as e:
            print(
                f"[{i}/{total}] PMCID={pmcid} ✗ failed to prepare input: {e}",
                flush=True,
            )
            stats["failed"] += 1
            failed_pmcids.append((pmcid, f"Input preparation: {e}"))
            continue

        # ===== STEP 2: Prepare prompt and examples =====
        if extraction_mode == "all":
            prompt = get_prompt_all()
            examples = get_fewshotexamples()
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
            examples = get_fewshotexamples()
            mode_label = f"guided ({len(icos)} ICOs)"

        else:
            raise ValueError(
                f"Invalid extraction_mode: {extraction_mode}. Use 'all' or 'guided'"
            )

        # ===== STEP 3: Run extraction =====
        label = f"[{i}/{total}] PMCID={pmcid} ({mode_label}) extracting…"

        is_gpt = model.startswith("gpt")
        is_gemini = model.startswith("gemini")

        extract_kwargs = {
            "text_or_documents": input_text,
            "prompt_description": prompt,
            "examples": examples,
            "model_id": model,
            "batch_length": 20,
            "extraction_passes": 2,
            "max_workers": 5,
        }

        if is_gpt:
            extract_kwargs.update({
                "fence_output": True,
                "use_schema_constraints": False,
            })
        else:
            extract_kwargs.update({
                "fence_output": True,
                "use_schema_constraints": True,
            })
        
        try:
            # Retry logic for quota errors
            max_attempts = 3
            extraction_successful = False
            
            result = None

            for attempt in range(1, max_attempts + 1):
                try:
                    with Spinner(label):
                        result = lx.extract(**extract_kwargs) #run actual extraction
                    extraction_successful = True
                    break
                except Exception as e:
                    msg = str(e)
                    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                        wait = 60 * attempt
                        print(
                            f"[{i}/{total}] PMCID={pmcid} quota error (attempt {attempt}/{max_attempts}), waiting {wait}s…",
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

            # Save to extractions subfolder
            lx.io.save_annotated_documents(
                [result],
                output_name=output_name,
                output_dir=extractions_folder,
            )
            print(
                f"[{i}/{total}] PMCID={pmcid} ✓ saved to extractions/{output_name}",
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

        # ===== STEP 4: Visualize =====
        try:
            # Pass the extractions folder and visualizations folder
            visualize(
                pmcid, 
                extractions_dir=extractions_folder,
                visualizations_dir=visualizations_folder,
                suffix=suffix, 
                model=model, 
                mode=extraction_mode
            )
        except Exception as e:
            print(
                f"[{i}/{total}] PMCID={pmcid} ⚠ visualization failed: {e}",
                flush=True,
            )

    # ===== Print extraction summary =====
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Total articles: {stats['total']}")
    print(f"Successfully processed: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped (no ICOs): {stats['skipped']}")
    
    if failed_pmcids:
        print(f"\nFailed PMCIDs:")
        for pmcid, reason in failed_pmcids:
            print(f"  PMCID={pmcid}: {reason}")
    
    print("=" * 80)

    # ===== Run evaluation if requested =====
    if run_evaluation and stats["successful"] > 0:
        print("\n" + "=" * 80)
        print("RUNNING EVALUATION")
        print("=" * 80)
        
        try:
            evaluator = BatchEvaluator(
                gold_path="gold-standard/annotated_rct_dataset.json",
                output_dir=evaluation_folder
            )
            
            results = evaluator.evaluate_directory(
                predictions_dir=extractions_folder,  # Point to extractions subfolder
                suffix_filter=suffix,
                run_name=run_name
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
    Example usage with different configurations.
    """
    
    # Example 1: Run guided extraction with evaluation
    run_lang_extract_with_eval(
        model="gemini-2.5-flash",
        extraction_mode="guided",
        run_evaluation=True,
        run_name=None
    )


if __name__ == "__main__":
    main()