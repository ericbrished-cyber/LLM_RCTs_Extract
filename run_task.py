
from run_lang_extract_with_evaluation import run_lang_extract_with_eval
from run_GPT5_direct_with_evaluation import run_gpt5_with_eval


# Main three runs

#Run 1: LangExtract with Gemini 2.5 Flash (guided mode)
# from run_lang_extract_with_evaluation import run_lang_extract_with_eval
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
#     run_evaluation=True,
#     run_name=None  # Auto-generates: LangExtract_gemini_2_5_flash_guided
# )

# Run 2: LangExtract with GPT-5 Mini (guided mode)
# run_lang_extract_with_eval(
#     model="gpt-5-mini",
#     extraction_mode="guided",
#     run_evaluation=True,
#     run_name=None  # Auto-generates: LangExtract_gpt_5_mini_guided
# )

# Run 3: GPT5 Direct (no LangExtract) with GPT-5.1 (guided mode)
run_gpt5_with_eval(
    model="gpt-5.1",
    extraction_mode="guided",
    run_evaluation=True,
    run_name=None  # Auto-generates: GPT5Direct_gpt_5_1_guided
)
