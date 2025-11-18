# Prompt
You are extracting **numerical statistical results** from a randomized controlled trial. Return **only** JSON of the form: `{"extractions":[ ... ]}`.

- Use `extraction_class` to encode *what* the number is (e.g. `intervention_mean`).
- Use `attributes` to encode *who/what* it belongs to (`Intervention`, `Comparator`, `Outcome`, and any other disambiguating attributes such as `Timepoint` or `Population` when needed).

## What to annotate
You are given a list of target ICO triplets:

{ico_list}

Each ICO triplet is defined by `(Intervention, Comparator, Outcome)` (and optionally additional attributes like `Timepoint` or `Population`).

For **each such ICO triplet, and only these**:
- **Continuous outcomes**  
  Extract (when reported):  
  - `total_group_size`
  - `intervention_group_size`
  - `comparator_group_size`
  - `intervention_mean`
  - `comparator_mean`
  - `total_mean`
  - `intervention_standard_deviation`
  - `comparator_standard_deviation`
  - `total_standard_deviation`

- **Binary outcomes**
  Extract (when reported):
  - `intervention_group_size`
  - `comparator_group_size`
  - `total_group_size`
  - `intervention_events`
  - `comparator_events`
  - `total_events`
  - `intervention_rate`
  - `comparator_rate`
  - `total_rate`

- **ICO identity**  
  - Merge duplicates that differ only in wording (e.g., "death or MI" ≈ "death or myocardial infarction").  
  - ALWAYS set the appropriate `Intervention`, `Comparator`, and `Outcome` attributes for every extraction that belongs to an ICO.

> Do **NOT** extract data for interventions, comparators, or outcomes that are not in `{ico_list}`.

---
## Consistency & numeric rules (very important)

Think of each ICO + metric as a **single cell in a table**. For each such cell:

- **One value per ICO + metric**  
  For a given ICO context (Intervention/Comparator + Outcome + any extra disambiguating attributes like Timepoint/Population) and `extraction_class`, you may output **at most one** numeric value.  
  - Example: If `comparator_mean = 38` for `I=Paracetamol, C=Placebo, O=Body temperature (°C)`, you must NOT also output `comparator_mean = 39` for the same ICO context.
  - Do not produce two extractions with the same ICO and `extraction_class` but different numbers.