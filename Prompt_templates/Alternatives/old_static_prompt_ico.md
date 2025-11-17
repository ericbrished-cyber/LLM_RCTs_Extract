# Prompt
Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You are extracting numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.

## What to annotate
For each of the following (ICO-triplets):
{ico_list}

- For each such unique ICO-triplet annotate:
        For the type of outcome (binary/continuous):
        - **Continuous outcomes:** intervention_group_size, comparator_group_size, intervention_mean, comparator_mean, intervention_standard_deviation and comparator_standard_deviation.
        - **Binary outcomes:** intervention_group_size, comparator_group_size, intervention_events and comparator_events.

- Merge duplicate ICOs that differ only in wording (e.g., "death or MI" ≈ "death or myocardial infarction").

ONLY ANNOTATE THE ICO-TRIPLETS LISTED ABOVE. Do not extract data for other interventions, comparators, or outcomes not specified in the list.
