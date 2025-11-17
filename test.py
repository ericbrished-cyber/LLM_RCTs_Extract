import json
import langextract as lx
from pathlib import Path

from utils import get_icos, list_pmcids, get_fewshotexamples_static, get_xml, get_prompt_static, get_fulltext


get_fulltext(3648394)