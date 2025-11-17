Imagine you are a meta-analysis expert and expert on experimental design. Use this knowledge to grasp what the researchers actually did in the RCT. Using this baseline understanding move on with further tasks.

You're task is to extract numerical statistical results from a randomized controlled trial. Return JSON with {'extractions':[...]} only.

ONLY ANNOTATE THESE THINGS:
For the type of outcome (binary/continuous):
         - **Continuous outcomes:** intervention_group_size, comparator_group_size, intervention_mean, comparator_mean, intervention_standard_deviation and comparator_standard_deviation.
        - **Binary outcomes:** intervention_group_size, comparator_group_size, intervention_events, comparator_events, comparator_rate, and intervention_rate.

