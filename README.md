# LLM_RCTs_Extract
Evaluating how well Lang Extract and GPT5 extract statistical data from randomized controlled trials. 

## Export predictions to Excel

Convert LangExtract JSONL outputs into a spreadsheet with one row per ICO triplet and one column per field:

```bash
python export_extractions_to_excel.py \
  --input outputs/LangExtract_gpt_5_mini_guided/extractions \
  --output outputs/gpt5_mini_guided.xlsx \
  --suffix _guided
```

- `--input`: folder containing the `.jsonl` extraction files for a run.
- `--suffix`: optional filter for filenames (e.g., `_guided` or `_all`); omit if you want every JSONL in the folder.
- The Excel file will include `pmcid`, `intervention`, `comparator`, `outcome`, and each numeric field (`intervention_group_size`, `intervention_mean`, etc.) as separate columns.
