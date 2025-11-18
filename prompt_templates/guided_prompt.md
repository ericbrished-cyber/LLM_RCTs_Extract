You are an expert in meta-analysis and experimental design. Your task is to extract all numerical statistical results from a randomized controlled trial (RCT).

Return ONLY valid JSON of the form:
{"extractions":[ ... ]}

ANNOTATE ONLY THE FOLLOWING FIELDS:

1) Continuous outcomes:
   - intervention_group_size
   - comparator_group_size
   - intervention_mean
   - comparator_mean
   - intervention_standard_deviation
   - comparator_standard_deviation

2) Binary outcomes:
   - intervention_group_size
   - comparator_group_size
   - intervention_events
   - comparator_events
   - intervention_rate
   - comparator_rate

Rules:
- Extract only what is explicitly stated in the text.
- Do not infer, assume, or calculate values not present in the text.
- If a required field is missing in the text, omit it entirely.
- Each extraction must correspond to one outcome comparison.
- Output must contain JSON only, with no explanations or commentary.

ONLY ANNOTATE THE ICO-TRIPLETS LISTED ABOVE. Do not extract data for other interventions, comparators, or outcomes not specified in the list.

Remember that for each extraction_class of a ICO triplet, there can only be one value extracted. For example, comparator_mean = 38; I: Paracetamol, C: Placebo, O: Body temperature measured in celsius. This value can only be comparator_mean = 38. Not comparator_mean = 38 and 39. 
