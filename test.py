import json
import langextract as lx

from utils import get_icos, list_pmcids

pmcid_lst = list_pmcids(pdf_folder = "data/PDF")

print(pmcid_lst)

for pmcid in pmcid_lst:
        print(get_icos(pmcid))

