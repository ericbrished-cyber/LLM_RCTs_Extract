# Prompt
You are extracting study data. Output **JSON only** following the schema. Capture **all ICO triplets** and, for each outcome, numeric data for both arms.

## What to extract
- All distinct **(Intervention, Comparator, Outcome)** combinations.
- **Continuous outcomes:** `n`, `mean`, `sd` per arm.
- **Binary outcomes:** `n`, `events` per arm.