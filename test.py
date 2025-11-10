import json

from utils import simplified_entry, get_xml, pdf_to_markdown


pdf_to_markdown()



with open('gold-standard/annotated_rct_dataset.json', 'r') as file:
        ICOs = json.load(file)
for entry in ICOs:
    simpl = simplified_entry(entry)


