import json
import langextract as lx

import json

with open('gold-standard/annotated_rct_dataset.json', 'r') as f:
    annotations = json.load(f)


pmcid = 5459356
dict = {}
for entry in annotations:               
   if entry["pmcid"] == 5459456:
       dict = {entry["id"]: [entry["intervention"], entry["comparator"], entry["outcome"]]}
print(dict)

