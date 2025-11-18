# Prompt

Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You are extracting numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.

## What to annotate
For each of the following (ICO-triplets):
{ico_list}

- For each such unique ICO-triplet annotate:
        - **Continuous outcomes:** intervention_group_size, comparator_group_size, intervention_mean, comparator_mean, intervention_standard_deviation and comparator_standard_deviation.
        - **Binary outcomes:** intervention_group_size, comparator_group_size, intervention_events, comparator_events, comparator_rate, and intervention_rate.

- Merge duplicate ICOs that differ only in wording (e.g., "death or MI" ≈ "death or myocardial infarction").

ONLY ANNOTATE THE ICO-TRIPLETS LISTED ABOVE. Do not extract data for other interventions, comparators, or outcomes not specified in the list.

Remember that for each extraction_class of a ICO triplet, there can only be one value extracted. For example, comparator_mean = 38; I: Paracetamol, C: Placebo, O: Body temperature measured in celsius. This value can only be comparator_mean = 38. Not comparator_mean = 38 and 39. 