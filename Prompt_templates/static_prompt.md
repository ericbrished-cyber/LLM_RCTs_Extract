# Prompt
You are extracting study data. Output **JSON only** following the schema. Capture **all ICO triplets** and, for each outcome, numeric data for both arms.

## What to extract
- All distinct **(Intervention, Comparator, Outcome)** combinations.

- For each such unique ICO extract:
    If outcome is continuous
        - **Continuous outcomes:** `n`, `mean`, `sd` per arm.
    If outcome is binary
        - **Binary outcomes:** `n`, `events` per arm.

Extract nothing more. ONLY THESE VALUES.