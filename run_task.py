from utils import get_prompt, get_fewshotexamples, get_xml, list_pmcids, get_icos, get_prompt_static

import json
import os
import langextract as lx

# run_task.py
import os
from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv())

API_KEY = os.getenv("LANGEXTRACT_API_KEY")

pdf_folder = "data/PDF_test"
output_folder = "./outputs"


pmcid_lst = list_pmcids(pdf_folder)

def run_task(model = "gemini-2.5-flash"):

    for pmcid in pmcid_lst:

        # 1. Define the prompt and extraction rules
        prompt = get_prompt_static()
        # The input text to be processed
        input_text = get_xml(pmcid)

        # 2. Provide a high-quality example to guide the model
        examples = get_fewshotexamples(pmcid)

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

        lx.io.save_annotated_documents([result], output_name="extraction_results.jsonl", output_dir=output_folder)
   


run_task(model="gpt-5-mini")