## Quick orientation

This repository extracts numerical/statistical results from randomized controlled trials using LangExtract and PDF/XML inputs. Key entrypoints and components:

- `run_task.py` — main driver. Prepares input (XML or PDF->Markdown), constructs prompts/examples via `utils.py`, calls `langextract` (`lx.extract`) and saves outputs to `./outputs`.
- `utils.py` — helper functions: listing PMCIDs from PDF filenames (`list_pmcids`), loading prompts (`get_prompt_static`, `get_prompt_with_icos`), loading few-shot examples (`get_fewshotexamples_static`), and loading gold-standard ICO annotations (`get_icos`). Also contains `visualize()` to produce HTML via `lx.visualize()`.
- `pdf_converter.py` — multi-stage PDF→Markdown conversion: prefers `pymupdf4llm`, falls back to layout-aware `pymupdf.layout`, then simple text extraction. Handles known pymupdf4llm failure modes.
- `XML_from_PMC.py` — downloads PMC full-text XML using Biopython Entrez (`efetch`). Note: `Entrez.email` is set in the file and should be updated to a valid address for your usage.
- `gold-standard/annotated_rct_dataset.json` — annotations used by `get_icos()` (structure: id, pmcid, intervention, comparator, outcome, outcome_type).

## High-level dataflow

1. Input PDFs live in `data/PDF_test` (filenames must contain numeric PMCIDs; `list_pmcids()` accepts `1234567` or `PMCID1234567`).
2. For `source_type='pdf'`: `run_task` converts PDFs to Markdown into `data/Markdown` using `pdf_converter.convert_pdf_to_markdown()` then reads markdown with `get_fulltext()`.
3. For `source_type='xml'`: `run_task` will try to read `data/XML_fulltext/PMC{pmcid}.xml`; if missing it calls `XML_from_PMC.download_pmc_xml()`.
4. Prompts and few-shot examples are loaded from `prompt_templates/` (see `static_prompt.md`, `static_prompt_ico.md`, `few-shots/examples*.yaml`).
5. Extraction: `langextract` (`lx.extract`) is called with examples and prompt. Results are saved with `lx.io.save_annotated_documents()` to `./outputs` using the naming pattern `{pmcid}_{extraction_mode}_{source_type}.jsonl`.
6. `utils.visualize()` creates an HTML visualization in `./outputs` named like `visualization_{pmcid...}.html`.

## Important repository conventions & gotchas (agent-focused)

- PMCID handling: filenames sometimes use `PMCID{num}.pdf` or just `{num}.pdf`. Use `utils.list_pmcids()` to discover IDs rather than assuming a naming style.
- Markdown/XML lookup is strict: `get_fulltext()` looks for `{pmcid}.md` in the markdown folder, `get_xml()` expects `PMC{pmcid}.xml`. When adding files, make sure names match these patterns.
- The project uses `python-dotenv` and `run_task.py` calls `load_dotenv(find_dotenv())` early — keep secrets/API keys out of source and place them in a `.env` file at the repo root if needed. No specific env var names are referenced in code; examine `langextract`/provider SDK docs for required keys.
- `XML_from_PMC.py` sets `Entrez.email` inline. Change this to your email before heavy use of NCBI Entrez and avoid hardcoding credentials in shared commits.
- PDF conversion: `pymupdf4llm` is the preferred converter. Known failure mode (`min() iterable is empty`) is explicitly handled in `pdf_converter.py` — prefer not to change that logic unless you add new fallbacks.
- `run_task.py` final lines currently call `run_task(source_type="pdf", extraction_mode="guided")` (note: small indentation oddity). When editing, be careful not to unintentionally change whether the module runs on import.

## How to run (developer workflows)

1. Create an isolated environment (venv/conda) and install dependencies:

```
python -m pip install -r requirements.txt
```

2. Prepare data:
 - Put PDFs into `data/PDF_test/` (filenames must include PMCID). Or place full-text XML files under `data/XML_fulltext/PMC{pmcid}.xml`.
 - Confirm `gold-standard/annotated_rct_dataset.json` exists (used for guided mode).

3. Run extraction (example):

```
python run_task.py   # default in-repo example calls guided PDF run
# or import and call programmatically:
# from run_task import run_task
# run_task(model="gpt-5-mini", source_type="xml", extraction_mode="all")
```

Outputs: `./outputs/{pmcid}_{mode}_{source_type}.jsonl` and visualization HTML files in `./outputs`.

## API keys / provider configuration

This project uses LangExtract which (for Gemini/Vertex) requires credentials. You can provide credentials via environment variables or a `.env` file (the repo already calls `load_dotenv(find_dotenv())`).

- To use Gemini via API key (recommended for quick local runs):

```
# macOS / zsh
export LANGEXTRACT_API_KEY="your-gemini-api-key-here"
python run_task.py
```

Or add a `.env` file at the repo root:

```
LANGEXTRACT_API_KEY=your-gemini-api-key-here
```

- To use Vertex AI instead of a raw API key, set these environment variables (or add them to `.env`):

```
LANGEXTRACT_VERTEX_PROJECT=your-gcp-project-id
LANGEXTRACT_VERTEX_LOCATION=your-vertex-location
```

The `run_task.py` script will automatically pass either the API key or the Vertex config into `lx.extract()` when present.

## Code patterns to follow when modifying/adding code

- Prefer using helpers in `utils.py` to load prompts, examples and ICOs — that centralizes file paths and parsing.
- When changing prompt templates, update `prompt_templates/static_prompt.md` and `prompt_templates/static_prompt_ico.md` together; `get_prompt_with_icos()` formats ICO lists into the static template when available.
- For PDF conversion changes, keep the staged approach (pymupdf4llm → layout → simple) and preserve the existing error handling so conversions remain robust.
- When adding new CLI flags or options to `run_task.py`, maintain backward compatibility with existing function signature: `run_task(model, source_type, extraction_mode)`.

## Integration & external dependencies

- Primary ML/LLM integration: `langextract` (see `requirements.txt` for version pinned). `run_task.py` passes `model_id`, `fence_output`, and `use_schema_constraints` to `lx.extract` — these were chosen for GPT-5 compatibility.
- PDF parsing: `pymupdf4llm`, `PyMuPDF` and `pymupdf-layout` are used; installing matching binary wheels for your platform is required (see `requirements.txt`).
- XML download: NCBI Entrez via Biopython (`Bio.Entrez.efetch`) — set `Entrez.email` and respect NCBI rate limits.

## Small examples to copy/paste

- Access ICOs for PMCID 4357072 in code:

```py
from utils import get_icos
print(get_icos(4357072))
```

- Convert a single PDF and get markdown path:

```py
from pdf_converter import convert_pdf_to_markdown
convert_pdf_to_markdown('data/PDF_test/4357072.pdf', output_dir='data/Markdown')
```

## If you change public behavior

- Update `README.md` and add small unit or smoke tests (project currently lacks automated test harness). Keep changes minimal and avoid renaming the `outputs/` or `data/` layout without updating the helper functions in `utils.py` and `run_task.py`.

---

If anything in this summary is unclear or you want additional examples (e.g., sample `.env` keys to set for a specific LLM provider), tell me which area to expand and I will iterate. 
