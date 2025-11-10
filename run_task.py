import langextract as lx
from utils import get_prompt, get_fulltext, get_fewshotexamples, simplified_entry, get_xml
import json

def run_task(model):
    #load JSON file
    with open('gold-standard/annotated_rct_dataset.json', 'r') as file:
        annotations = json.load(file)

    for entry in annotations:
        #only keep, relevant data: id of ICO, PMCID, I, C, O and binary/continuous type
        simpl_entry = simplified_entry(entry)

        # 1. Define the prompt and extraction rules
        prompt = get_prompt(simpl_entry)

        # 2. Provide a high-quality example to guide the model
        # The input text to be processed
        input_text = get_xml(simpl_entry)

        examples = get_fewshotexamples(simpl_entry)

        # Run the extraction
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id=model,
        )

