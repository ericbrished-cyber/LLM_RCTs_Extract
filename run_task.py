import time, threading, os, time

from utils import (
    get_xml, 
    get_fulltext, 
    list_pmcids, 
    get_icos, 
    get_prompt_all, 
    get_prompt_guided,
    get_fewshotexamples, 
    visualize,
)

from spinner import Spinner

from pdf_converter import convert_pdf_to_markdown
from XML_from_PMC import download_pmc_xml
import json

try:
    import langextract as lx
except Exception:
    lx = None

from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv())

pdf_folder = "data/PDF_test"
markdown_folder = "data/Markdown"
xml_folder = "data/XML_fulltext"
output_folder = "./outputs"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(markdown_folder, exist_ok=True)
os.makedirs(xml_folder, exist_ok=True)

pmcid_lst = list_pmcids(pdf_folder)





def run_task(
    model="gemini-2.5-flash",
    source_type="xml",  # "xml" or "pdf"
    extraction_mode="all",  # "all" or "guided"
):
    """
    Run extraction task on PMC articles.

    Args:
        model (str): Model identifier for langextract
        source_type (str): "xml" for XML files, "pdf" for PDF->Markdown conversion
        extraction_mode (str):
            - "all": Extract all statistical information (no ICO guidance)
            - "guided": Extract specific ICOs given in annotations
    """
    total = len(pmcid_lst)

    if lx is None:
        raise ImportError(
            "Missing dependency: 'langextract' is not installed. "
            "Install project dependencies with: python -m pip install -r requirements.txt"
        )

    print(f"Found {total} PDFs. Output → {os.path.abspath(output_folder)}", flush=True)
    print(f"Mode: source={source_type.upper()}, extraction={extraction_mode}", flush=True)
    print()

    for i, pmcid in enumerate(pmcid_lst, 1):
        # ===== STEP 1: Prepare input text =====
        try:
            if source_type == "xml":
                input_text = get_xml(pmcid, xml_folder_path=xml_folder)
                if input_text.startswith("XML file for PMCID"):
                    print(
                        f"[{i}/{total}] PMCID={pmcid} - XML not found, downloading.",
                        flush=True,
                    )
                    xml_path = download_pmc_xml(pmcid, output_dir=xml_folder)
                    if xml_path:
                        input_text = get_xml(pmcid, xml_folder_path=xml_folder)
                    else:
                        print(
                            f"[{i}/{total}] PMCID={pmcid} ✗ failed to download XML",
                            flush=True,
                        )
                        continue
            
            elif source_type == "pdf":
                pdf_path = os.path.join(pdf_folder, f"{pmcid}.pdf")
                if not os.path.exists(pdf_path):
                    pdf_path = os.path.join(pdf_folder, f"PMCID{pmcid}.pdf")

                if not os.path.exists(pdf_path):
                    print(
                        f"[{i}/{total}] PMCID={pmcid} ✗ PDF not found",
                        flush=True,
                    )
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
                    continue
            else:
                raise ValueError(
                    f"Invalid source_type: {source_type}. Use 'xml' or 'pdf'"
                )

        except Exception as e:
            print(
                f"[{i}/{total}] PMCID={pmcid} ✗ failed to prepare input: {e}",
                flush=True,
            )
            continue

        # ===== STEP 2: Prepare prompt and examples =====
        if extraction_mode == "all":
            # Extract all statistical information
            prompt = get_prompt_all()
            examples = get_fewshotexamples(xml=(source_type == "xml"))
            mode_label = "all stats"

        elif extraction_mode == "guided":
            icos = get_icos(pmcid)
            if not icos:
                print(
                    f"[{i}/{total}] PMCID={pmcid} ⚠ no ICOs in annotations, skipping",
                    flush=True,
                )
                continue
            
            prompt = get_prompt_guided(pmcid)  # Pass pmcid, not icos dict
            examples = get_fewshotexamples(xml=(source_type == "xml"))
            mode_label = f"guided ({len(icos)} ICOs)"

        else:
            raise ValueError(
                f"Invalid extraction_mode: {extraction_mode}. Use 'all' or 'guided'"
            )

        # ===== STEP 3: Run extraction =====
        label = f"[{i}/{total}] PMCID={pmcid} ({mode_label}) extracting…"

        is_gpt5 = model.startswith("gpt-5") or model.startswith("gpt-4.2")
        is_gemini = model.startswith("gemini")

        extract_kwargs = {
            "text_or_documents": input_text,
            "prompt_description": prompt,
            "examples": examples,
            "model_id": model,
            "extraction_passes": 1 if is_gemini else 2,
            # Free tier för Gemini tål inte många parallella anrop
            "max_workers": 1 if is_gemini else 10,
        }

        if is_gpt5:
            extract_kwargs.update(
                {
                    "fence_output": True,
                    "use_schema_constraints": False,
                }
            )
        else:
            extract_kwargs.update(
                {
                    "fence_output": False,
                    "use_schema_constraints": True,
                }
            )
        try:
            # Enkel retry vid kvotfel
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    with Spinner(label):
                        result = lx.extract(**extract_kwargs)
                    break  # lyckades, lämna retry-loopen
                except Exception as e:
                    msg = str(e)
                    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                        wait = 60 * attempt  # öka väntetiden vid varje försök
                        print(
                            f"[{i}/{total}] PMCID={pmcid} kvotproblem (försök {attempt}/{max_attempts}), väntar {wait} sekunder…",
                            flush=True,
                        )
                        time.sleep(wait)
                        continue
                    else:
                        # annat fel, kasta vidare
                        raise
            else:
                print(
                    f"[{i}/{total}] PMCID={pmcid} ✗ misslyckades efter {max_attempts} försök (kvotfel).",
                    flush=True,
                )
                continue

            print(
                f"[{i}/{total}] PMCID={pmcid} ✓ extracted. Saving…",
                flush=True,
            )

            suffix = f"_{extraction_mode}_{source_type}"
            output_name = f"{pmcid}{suffix}.jsonl"

            lx.io.save_annotated_documents(
                [result],
                output_name=output_name,
                output_dir=output_folder,
            )
            print(
                f"[{i}/{total}] PMCID={pmcid} ✓ saved {output_name}",
                flush=True,
            )

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
            continue

        # ===== STEP 4: Visualize =====
        try:
            visualize(pmcid, output_dir=f"{output_folder}/visualization", suffix=suffix)
        except Exception as e:
            print(
                f"[{i}/{total}] PMCID={pmcid} ⚠ visualization failed: {e}",
                flush=True,
            )

# Example usage
if __name__ == "__main__":
    # Extract all stats from XML
    # run_task(model="gpt-5-mini", source_type="xml", extraction_mode="all")

    # Extract all stats from PDF (via Markdown)
    # run_task(model="gpt-5-mini", source_type="pdf", extraction_mode="all")

    # Extract specific ICOs from XML
    # run_task(model="gpt-5-mini", source_type="xml", extraction_mode="guided")

    # Extract specific ICOs from PDF
    run_task(model="gemini-2.5-pro", source_type="pdf", extraction_mode="guided")
