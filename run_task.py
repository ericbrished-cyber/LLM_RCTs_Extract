
from run_lang_extract_with_evaluation import run_lang_extract_with_eval
from run_GPT5_direct_with_evaluation import run_gpt5_with_eval


# --- Quick knobs to turn between runs ---
PDF_FOLDER = "data/PDF_excel_test"
MARKDOWN_FOLDER = "data/Markdown"
BASE_OUTPUT_FOLDER = "./outputs"

# Swap these to try different prompting / examples
FEW_SHOTS_PATH = "few-shots/new_examples.yaml"  # e.g. "few-shots/examples.yaml"
PROMPT_ALL_PATH = "prompt_templates/all_prompt_new.md"
GUIDED_PROMPT_TEMPLATE = "prompt_templates/guided_prompt.md"

# Toggle evaluation once for all runs below
RUN_EVALUATION = True

# Main three runs

# #Run 1: LangExtract with Gemini 2.5 Flash (guided mode)
# run_lang_extract_with_eval(
#     model="gemini-2.5-pro",
#     extraction_mode="guided",
#     run_evaluation=True,
#     run_name=None  # Auto-generates: LangExtract_gemini_2_5_flash_guided
# )

# Run 2: LangExtract with GPT-5 Mini (guided mode)
# run_lang_extract_with_eval(
#     model="gpt-5-mini",
#     extraction_mode="guided",
#     run_evaluation=RUN_EVALUATION,
#     run_name=None,  # Auto-generates: LangExtract_gemini_2_5_flash_guided
#     pdf_folder=PDF_FOLDER,
#     markdown_folder=MARKDOWN_FOLDER,
#     base_output_folder=BASE_OUTPUT_FOLDER,
#     few_shots_path=FEW_SHOTS_PATH,
#     prompt_all_path=PROMPT_ALL_PATH,
#     guided_prompt_template=GUIDED_PROMPT_TEMPLATE,
# )

# Run 2: LangExtract with GPT-5 Mini (guided mode)
# run_lang_extract_with_eval(
#     model="gpt-5-mini",
#     extraction_mode="guided",
#     run_evaluation=True,
#     run_name=None  # Auto-generates: LangExtract_gpt_5_mini_guided
# )

# Run 3: GPT5 Direct (no LangExtract) with GPT-5.1 (guided mode)
# run_gpt5_with_eval(
#     model="gpt-5.1",
#     extraction_mode="guided",
#     run_evaluation=True,
#     run_name=None  # Auto-generates: GPT5Direct_gpt_5_1_guided
# )
