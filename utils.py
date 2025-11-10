import json
import os
import pdfplumber
import yaml

def get_prompt(entry):
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




def get_fulltext(entry, text_folder_path="data/TXT"):
    pmcid = entry["pmcid"]


def get_xml(entry, xml_folder_path="data/XML"):
    """
    Retrieves the XML content for the given PMCID.

    Args:
        entry (dict): The entry containing the PMCID.
        xml_folder_path (str): Path to the folder containing XML files.

    Returns:
        str: The content of the XML file if found, or an error message.
    """
    pmcid = entry["pmcid"]
    xml_file_path = os.path.join(xml_folder_path, f"PMC{pmcid}.xml")

    if os.path.exists(xml_file_path):
        with open(xml_file_path, "r", encoding="utf-8") as xml_file:
            return xml_file.read()
    else:
        return f"XML file for PMCID {pmcid} not found in {xml_folder_path}."

def get_fewshotexamples(entry, few_shots_folder="few-shots"):
    """
    Generates few-shot examples based on the entry's outcome type.

    Args:
        entry (dict): The entry containing the outcome type.
        few_shots_folder (str): Path to the folder containing few-shot YAML files.

    Returns:
        list: A list of few-shot examples formatted for langextract.
    """
    # Determine the appropriate YAML file based on outcome type
    if entry["outcome_type"] == "binary":
        yaml_file = os.path.join(few_shots_folder, "binary_examples.yaml")
    else:
        yaml_file = os.path.join(few_shots_folder, "continuous_examples.yaml")

    # Load the YAML file
    try:
        with open(yaml_file, "r", encoding="utf-8") as file:
            few_shot_data = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Few-shot YAML file not found: {yaml_file}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {yaml_file}: {e}")

    # Convert the YAML data into the correct format for langextract
    examples = []
    for example in few_shot_data.get("examples", []):
        examples.append({
            "text": example.get("text", ""),
            "extractions": example.get("extractions", [])
        })

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