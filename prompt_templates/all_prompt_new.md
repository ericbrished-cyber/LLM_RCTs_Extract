prompt_description: |
  You are an expert in meta-analysis and experimental design. Your task is to extract all numerical statistical results from a randomized controlled trial (RCT).

  Return ONLY valid JSON of the form:
  {"extractions":[ ... ]}

  Each item in "extractions" must describe one specific comparison between two study arms and may contain ONLY the following fields:

  Shared identifiers (include if present in the text):
    - outcome
    - intervention
    - comparator

  Continuous outcomes (include only if explicitly stated):
    - intervention_group_size
    - comparator_group_size
    - intervention_mean
    - comparator_mean
    - intervention_standard_deviation
    - comparator_standard_deviation

  Binary outcomes (include only if explicitly stated):
    - intervention_group_size
    - comparator_group_size
    - intervention_events
    - comparator_events
    - intervention_rate
    - comparator_rate

  Rules:
    1. Extract only what is explicitly stated in the text.
    2. Do not infer, calculate, or guess values.
    3. If a field is missing from the text, omit the field entirely.
    4. Do not output placeholder values such as "x", "", 0, null, or false.
    5. Each extraction must correspond to exactly one outcome comparison.
    6. Output must contain JSON only, with no explanations or commentary.
