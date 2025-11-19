import json
import os
import yaml
from pathlib import Path
import re
import langextract as lx
import glob

with open('gold-standard/annotated_rct_dataset.json', 'r') as file:
        annotations = json.load(file)

PMCID_RE = re.compile(r'(?:PMCID)?(\d{6,8})', re.IGNORECASE)

def list_pmcids(pdf_folder: str) -> list[str]:
    pmcids = []
    seen = set()
    for pdf_path in Path(pdf_folder).glob("*.pdf"):
        # try to pull a numeric PMCID from the filename (with or without PMCID prefix)
        m = PMCID_RE.search(pdf_path.stem)
        if not m:
            continue
        pmcid = m.group(1)
        if pmcid not in seen:
            seen.add(pmcid)
            pmcids.append(int(pmcid))
    return pmcids

def get_icos(pmcid):
    result = {
        e["id"]: [e["intervention"], e["comparator"], e["outcome"]]
        for e in annotations
        if e.get("pmcid") == pmcid
        }
    return result


def get_prompt_all():
    path = Path("prompt_templates/all_prompt.md")
    text = path.read_text(encoding="utf-8")
    return text


def get_fulltext(pmcid, text_folder_path="data/Markdown"):
    """
    Get the markdown content for a given PMCID.
    
    Args:
        pmcid (int or str): The PMCID to retrieve
        text_folder_path (str): Path to the folder containing markdown files
    
    Returns:
        str: Content of the markdown file, or error message if not found
    """
    md_file_path = os.path.join(text_folder_path, f"{pmcid}.md")
    
    if os.path.exists(md_file_path):
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            return md_file.read()
    else:
        return f"Markdown file for PMCID {pmcid} not found in {text_folder_path}."




def get_xml(pmcid, xml_folder_path="data/XML"):
    xml_file_path = os.path.join(xml_folder_path, f"PMC{pmcid}.xml")

    if os.path.exists(xml_file_path):
        with open(xml_file_path, "r", encoding="utf-8") as xml_file:
            return xml_file.read()
    else:
        return f"XML file for PMCID {pmcid} not found in {xml_folder_path}."

def _build_char_interval(item):
    """Create a CharInterval from a YAML dict if present."""
    ci = item.get("char_interval")
    if not ci:
        return None
    return lx.data.CharInterval(
        start_pos=ci["start_pos"],
        end_pos=ci["end_pos"],
    )


def get_fewshotexamples(few_shots_folder="few-shots", xml=False):
    """
    Load few-shot examples from a YAML file and convert them to LangExtract ExampleData.

    If `xml` is True, loads `examples_XML.yaml`, otherwise `examples.yaml`.
    """
    few_shots_folder = Path(few_shots_folder)
    yaml_filename = "examples_XML.yaml" if xml else "examples.yaml"
    yaml_file = few_shots_folder / yaml_filename

    with yaml_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    examples = []

    for ex in data.get("examples", []):
        text = ex["text"]
        extractions = []

        for item in ex.get("extractions", []):
            extractions.append(
                lx.data.Extraction(
                    extraction_class=item["extraction_class"],
                    extraction_text=item["extraction_text"],
                    attributes=item.get("attributes", {}),
                    char_interval=_build_char_interval(item),
                )
            )

        examples.append(
            lx.data.ExampleData(
                text=text,
                extractions=extractions,
            )
        )

    return examples


def simplified_entry(entry):
    simplified_entry = {
        "id": entry["id"],
        "pmcid": entry["pmcid"],
        "intervention": entry["intervention"],
        "comparator": entry["comparator"],
        "outcome": entry["outcome"],
        "outcome_type": entry["outcome_type"]
    }
    return simplified_entry

def get_prompt_guided(pmcid):
    """
    Generate a prompt with specific ICOs to extract for a given PMCID.
    Uses the existing get_icos() function to retrieve annotations.
    
    Args:
        pmcid (int or str): The PMCID to get ICOs for
    
    Returns:
        str: Prompt instructing extraction of specific ICOs
    """
    from pathlib import Path
    
    icos_dict = get_icos(pmcid)
    
    if not icos_dict:
        # Fallback to generic prompt if no ICOs found
        return get_prompt_all()
    
    # Format ICOs in the same style as static_prompt.md
    icos_list = []
    for entry_id, (intervention, comparator, outcome) in icos_dict.items():
        icos_list.append(f"    Intervention: {intervention}\n    Comparator: {comparator}\n    Outcome: {outcome}")
    
    icos_text = "\n\n".join(icos_list)
    
    # Load template and substitute ICOs
    template_path = Path("prompt_templates/guided_prompt.md")
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
        prompt = template.replace("{ico_list}", icos_text)
        return prompt
    else:
        print("No prompt template found!")


def visualize(pmcid, output_dir, suffix=""):
    """
    HTML-visualization of the Langextract output
    
    Args:
        pmcid: The PMCID of the article
        output_dir: Directory containing the JSONL files
        suffix: Optional suffix added to the filename (e.g., "_all_xml")
    """
    
    # 1) Try exact match with suffix
    path = os.path.join(output_dir, f"{pmcid}{suffix}.jsonl")
    
    # 2) If not found, try to find a close match
    if not os.path.exists(path):
        matches = sorted(glob.glob(os.path.join(output_dir, f"*{pmcid}*.jsonl")))
        if not matches:
            raise FileNotFoundError(f"No JSONL for PMCID={pmcid} in {output_dir}")
        path = matches[-1]  # pick the latest by name
    
    # 3) Visualize and write HTML
    html = lx.visualize(path)
    
    # Extract just the filename without extension for the output
    base_name = os.path.splitext(os.path.basename(path))[0]
    out_html = os.path.join(output_dir, f"visualization_{base_name}.html")
    
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(getattr(html, "data", html))  # handle Jupyter objects or plain str
    
    print(f"✔ Visualization written to: {os.path.abspath(out_html)}")


visualize(3276927, output_dir="outputs")
