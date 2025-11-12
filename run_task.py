from utils import get_prompt, get_fulltext, get_fewshotexamples, simplified_entry, get_xml

import json
import os
import langextract as lx

# run_task.py
import os
from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv())

# Now your key is available via os.getenv
API_KEY = os.getenv("LANGEXTRACT_API_KEY")

def run_task(model = "gemini-2.5-flash"):
    #load JSON file
    with open('gold-standard/annotated_rct_dataset_test.json', 'r') as file:
        annotations = json.load(file)

    for entry in annotations:
        #only keep relevant information: id of unique ICO, PMCID, Intervention, Comparator, Outcome and binary/continuous type
        simple_entry = simplified_entry(entry)

        # 1. Define the prompt and extraction rules
        prompt = get_prompt(simple_entry)
        
        # The input text to be processed
        input_text = get_xml(simple_entry)

        # 2. Provide a high-quality example to guide the model
        examples = get_fewshotexamples(simple_entry)

        # Run the extraction
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id=model,
            api_key=os.environ.get('OPENAI_API_KEY'),
            fence_output=True,
            use_schema_constraints=False,
        )

        lx.io.save_annotated_documents([result], output_name="extraction_results.jsonl", output_dir=".")
   
run_task(model="gpt-5-mini")

