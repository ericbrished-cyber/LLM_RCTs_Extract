# Prompt

You are an expert in meta-analysis and experimental design. Extract **only** the following two fields from a randomized controlled trial (RCT):

- `intervention_group_size`
- `comparator_group_size`

Return **ONLY** valid JSON of the form:

```json
{"extractions":[ ... ]}
