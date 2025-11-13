import json
import os
import pdfplumber
import yaml
from pathlib import Path
import re
import langextract as lx

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


def get_prompt_static():
    path = Path("prompt_templates/static_prompt.md")
    text = path.read_text(encoding="utf-8")
    return text

def get_prompt(pmcid):
    ICOs = get_icos(pmcid)

    # Logic to generate the prompt based on the entry
    if entry["outcome_type"] == "binary":
        with open('prompt_templates/templates_binary.yaml', 'r') as binary_template_file:
            binary_template = binary_template_file.read()
        return binary_template.replace("{{intervention}}", entry["intervention"]) \
                              .replace("{{comparator}}", entry["comparator"]) \
                              .replace("{{outcome}}", entry["outcome"])
    else:
        with open('prompt_templates/templates_continuous.yaml', 'r') as continuous_template_file:
            continuous_template = continuous_template_file.read()
        return continuous_template.replace("{{intervention}}", entry["intervention"]) \
                                  .replace("{{comparator}}", entry["comparator"]) \
                                  .replace("{{outcome}}", entry["outcome"])



#def get_fulltext(pmcid, text_folder_path="data/TXT"):



def get_xml(pmcid, xml_folder_path="data/XML"):
    xml_file_path = os.path.join(xml_folder_path, f"PMC{pmcid}.xml")

    if os.path.exists(xml_file_path):
        with open(xml_file_path, "r", encoding="utf-8") as xml_file:
            return xml_file.read()
    else:
        return f"XML file for PMCID {pmcid} not found in {xml_folder_path}."


##FIXA SÅ KLARAR ATTRIBUTES OCKSÅ
def get_fewshotexamples(pmcid, few_shots_folder="few-shots"):
    yaml_file = os.path.join(
        few_shots_folder,
        "binary_examples.yaml" if entry.get("outcome_type") == "binary" else "continuous_examples.yaml"
    )

    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    examples = []
    for ex in data.get("examples", []):
        extractions = [
            lx.data.Extraction(
                extraction_class=it["extraction_class"],
                extraction_text=it["extraction_text"]
            )
            for it in ex.get("extractions", [])
        ]

        examples.append(lx.data.ExampleData(text=ex["text"], extractions=extractions))

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


