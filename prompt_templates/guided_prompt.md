# Prompt

You are extracting **numerical statistical results** from a randomized controlled trial. Return **only** JSON of the form: `{"extractions":[ ... ]}`.

- Use `extraction_class` to encode *what* the number is (e.g. `intervention_mean`).
- Use `attributes` to encode *who/what* it belongs to (`Intervention`, `Comparator`, `Outcome`, and any other disambiguating attributes such as `Timepoint` or `Population` when needed).

You are given a list of target ICO triplets:

{ico_list}

Each ICO triplet is defined by `(Intervention, Comparator, Outcome)` (and optionally additional attributes like `Timepoint` or `Population`).
