You are an expert in meta-analysis and experimental design.  
Extract **pairwise ICO results** from the Abstract and Results sections of a randomized controlled trial (RCT).

Return ONLY JSON:
{"extractions":[ ... ]}

Each item in "extractions" must be one ICO row with EXACTLY these fields (use null for any missing/not applicable):
{
  "id": null,
  "evidence_inference_prompt_id": null,
  "pmcid": "<STRING OR INTEGER>",
  "outcome": "<STRING>",
  "intervention": "<STRING>",
  "comparator": "<STRING>",
  "outcome_type": "<continuous | binary>",
  "intervention_events": null,
  "intervention_group_size": null,
  "comparator_events": null,
  "comparator_group_size": null,
  "intervention_mean": null,
  "intervention_standard_deviation": null,
  "comparator_mean": null,
  "comparator_standard_deviation": null
}

Rules:
- One JSON object per ICO triplet in `{ico_list}` for PMCID `{pmcid}`.
- Fill numeric fields that are explicitly reported; leave the rest null.
- Use plain numbers (no percent signs, no units).
- If no values are reported for a triplet, omit that triplet entirely.
- Output raw JSON only (no markdown fencing, no text).