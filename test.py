"""
Test suite for extraction pipeline capabilities.
Run individual tests or all tests to verify system functionality.
"""

import os
import sys
from pathlib import Path
import json
from utils import (
    list_pmcids,
    get_xml,
    get_fulltext,
    get_icos,
    get_prompt_all,
    get_prompt_guided,
    get_fewshotexamples
)
from pdf_converter import convert_pdf_to_markdown
from XML_from_PMC import download_pmc_xml

examples = get_fewshotexamples()

# ex0 = examples[0]

# print(repr(ex0.text[40:80]))
# print(repr(ex0.text[51:53]))

# for e in ex0.extractions:
#     print(e)

def check_example_alignment(examples):
    for i, ex in enumerate(examples):
        for j, e in enumerate(ex.extractions):
            ci = e.char_interval
            if ci is None:
                continue
            s, epos = ci.start_pos, ci.end_pos
            span = ex.text[s:epos]
            if span != e.extraction_text:
                print(
                    f"[example#{i} extraction#{j}] "
                    f"class={e.extraction_class!r} text={e.extraction_text!r} "
                    f"span={span!r} char_interval=({s}, {epos})"
                )

check_example_alignment(examples)