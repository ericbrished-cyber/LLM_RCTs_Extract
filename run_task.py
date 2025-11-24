from run_lang_extract_with_evaluation import run_lang_extract_with_eval
from run_GPT5_direct_with_evaluation import run_gpt5_with_eval


#Main three runs

# run_lang_extract_with_eval(
#         model="gemini_3_pro",
#         extraction_mode="guided",
#         run_evaluation=True,
#         run_name=None
#     )

# run_lang_extract_with_eval(
#         model="gpt-5-mini",
#         extraction_mode="guided",
#         run_evaluation=True,
#         run_name=None
#     )

run_gpt5_with_eval( #Direct GPT5 no lang extract
        model="gpt-5.1",
        extraction_mode="guided", # or "all"
        run_evaluation=True,
        run_name="gpt5_direct_pdf_guided",
    )