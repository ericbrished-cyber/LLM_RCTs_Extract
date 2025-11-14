# Prompt

Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You are extracting numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.


## What to annotate
- Find all distinct **(Intervention, Comparator, Outcome)** combinations (ICO-triplets). Make sure to not be too fine-grained. Try to grasp the general setup of the study and its ICO triplets and not associate every new way of reporting on what was done with a new ICO triplet.

ONLY ANNOTATE THESE THINGS:
- For each such unique ICO-triplet annotate:
        For the type of outcome (binary/continuous):
        - **Continuous outcomes:** group_size_intervention, group_size_comparator, mean_intervention, mean_comparator, sd_intervention and sd_comparator.
        - **Binary outcomes:** group_size_intervention, group_size_comparator, events_intervention and events_comparator.

- Merge duplicate ICOs that differ only in wording (e.g., “death or MI” ≈ “death or myocardial infarction”).