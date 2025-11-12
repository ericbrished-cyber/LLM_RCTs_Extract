import json
import langextract as lx

from utils import get_prompt, get_fulltext, get_fewshotexamples, simplified_entry, get_xml

with open('gold-standard/annotated_rct_dataset_test.json', 'r') as file:
        annotations = json.load(file)
        
for entry in annotations:
        #print(entry)
        simple_entry = simplified_entry(entry)
       # print(get_prompt(simple_entry))
        #print(get_xml(simple_entry))
        print(get_fewshotexamples(simple_entry))

html_content = lx.visualize("extraction_results.jsonl")
