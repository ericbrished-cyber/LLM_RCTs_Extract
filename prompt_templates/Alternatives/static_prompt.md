# Prompt

Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You are extracting numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.


## What to annotate
For each of the following (ICO-triplets):
    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:LF:HF component of HRV

    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:Push-up test

    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:Quality of life - PCS (SF36)

    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:Quality of life - MCS (SF36)

    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:NN50

    Intervention: 10-week yoga program
    Comparator: Control
    Outcome:Flexibility

- For each such unique ICO-triplet annotate:
        For the type of outcome (binary/continuous):
        - **Continuous outcomes:** group_size_intervention, group_size_comparator, mean_intervention, mean_comparator, sd_intervention and sd_comparator.
        - **Binary outcomes:** group_size_intervention, group_size_comparator, events_intervention and events_comparator.

- Merge duplicate ICOs that differ only in wording (e.g., “death or MI” ≈ “death or myocardial infarction”).