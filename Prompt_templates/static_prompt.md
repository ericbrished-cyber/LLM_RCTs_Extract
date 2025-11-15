# Prompt

Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You're task is to extract numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.

ONLY ANNOTATE THESE THINGS:
For the type of outcome (binary/continuous):
        - **Continuous outcomes:** group_size_intervention, group_size_comparator, mean_intervention, mean_comparator, sd_intervention and sd_comparator.
        - **Binary outcomes:** group_size_intervention, group_size_comparator, events_intervention and events_comparator.

Only raw numbers are preferred. For instance if a group_size is presented as n=20, extract just the number: 20.