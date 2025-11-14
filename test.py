import json
import langextract as lx
from pathlib import Path

from utils import get_icos, list_pmcids, get_fewshotexamples_static

pmcid_lst = list_pmcids(pdf_folder = "data/PDF")

print(get_fewshotexamples_static())