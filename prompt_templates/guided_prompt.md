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

## Consistency & numeric rules (very important)

Treat each **arm + outcome + metric** as a single table cell.

An arm-context is defined as:

  (Outcome) + (either Intervention or Comparator) + (any extra disambiguating attributes like Timepoint or Population)

For each such arm-context and `extraction_class`, you may output **at most z** numeric value.

Examples:
- For Outcome = "Treatment-emergent adverse events (TEAEs)" and Intervention = "desvenlafaxine",
  you may extract at most one `intervention_group_size`, one `intervention_events`, and one `intervention_rate`.
- For Outcome = "Mean body weight gain" and Comparator = "WA",
  you may extract at most one `comparator_mean` and one `comparator_standard_deviation`.

Do **NOT** produce two extractions with the same (Outcome, Intervention/Comparator, Timepoint/Population if relevant, `extraction_class`) but different numbers.

### ICO identity

You are only interested in the ICO triplets listed in `{ico_list}`.

- Always set `Outcome` for every extraction.
- For `intervention_*` classes:
  - Always set `Intervention`.
  - Set `Comparator` only if it is clearly identifiable in the local context (otherwise omit it).
- For `comparator_*` classes:
  - Always set `Comparator`.
  - Set `Intervention` only if it is clearly identifiable in the local context (otherwise omit it).
- For `total_*` classes:
  - Set `Outcome` and, if available, a `Population` attribute (e.g. "all randomized", "safety population").

Do **NOT** extract data for interventions, comparators, or outcomes that are not given in prompt (ignoring minor wording differences like "death or MI" vs "death or myocardial infarction").
