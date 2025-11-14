import json
import langextract as lx
from pathlib import Path

from utils import get_icos, list_pmcids, get_fewshotexamples_static, get_xml, get_prompt_static

pmcid_lst = list_pmcids(pdf_folder = "data/PDF_test")
total = len(pmcid_lst)

for i, pmcid in enumerate(pmcid_lst, 1):
        label = f"[{i}/{total}] PMCID={pmcid} extracting…"
        print(get_prompt_static())
        print(get_xml(pmcid))
        print(get_fewshotexamples_static())