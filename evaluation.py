import json
from pathlib import Path
from math import isclose


# ------------------ normalisation helpers ------------------ #

def normalize_name(s):
    if s is None:
        return None
    return " ".join(str(s).lower().split())


def normalize_value(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"", "none", "nr", "not reported", "n/a", "na", "not extractable"}:
        return None
    if s.endswith("%"):
        s = s[:-1].strip()
    try:
        return float(s)
    except ValueError:
        return None


def get_pmcid_from_filename(path: str) -> int:
    name = Path(path).name
    digits = "".join(ch for ch in name if ch.isdigit())
    if not digits:
        raise ValueError(f"No digits (pmcid) in filename: {name}")
    return int(digits)


# ------------------ schema mapping ------------------ #

# map gold / extraction classes to a simple field name + role
CLASS_INFO = {
    # counts
    "intervention_events": ("I", "events"),
    "comparator_events":   ("C", "events"),

    # group sizes
    "intervention_group_size": ("I", "group_size"),
    "intervention_groupsize":  ("I", "group_size"),
    "group_size_intervention": ("I", "group_size"),

    "comparator_group_size": ("C", "group_size"),
    "comparator_groupsize":  ("C", "group_size"),
    "group_size_comparator": ("C", "group_size"),

    # means
    "intervention_mean": ("I", "mean"),
    "mean_intervention": ("I", "mean"),

    "comparator_mean": ("C", "mean"),
    "mean_comparator": ("C", "mean"),

    # SDs
    "intervention_standard_deviation": ("I", "sd"),
    "sd_intervention":                 ("I", "sd"),

    "comparator_standard_deviation": ("C", "sd"),
    "sd_comparator":                 ("C", "sd"),

    # rates (percentage outcomes)
    "intervention_rate": ("I", "rate"),
    "comparator_rate":   ("C", "rate"),
}


# ------------------ gold side: build arm-facts ------------------ #

def build_gold_arm_facts(gold_path: str, pmcid: int):
    """
    Return a set of arm-facts:
      (pmcid, outcome_norm, role, arm_name_norm, field, value)
    """
    with open(gold_path, "r", encoding="utf-8") as f:
        gold_rows = json.load(f)

    facts = set()

    for row in gold_rows:
        if int(row["pmcid"]) != int(pmcid):
            continue

        outcome = normalize_name(row.get("outcome"))
        I_name = normalize_name(row.get("intervention"))
        C_name = normalize_name(row.get("comparator"))

        # for each potential field in the gold row, map to arm-facts
        for cls, (role, field) in CLASS_INFO.items():
            raw_val = row.get(cls)
            val = normalize_value(raw_val)
            if val is None:
                continue

            if role == "I":
                arm = I_name
            else:
                arm = C_name

            if arm is None:
                continue  # weird, but be safe

            fact = (pmcid, outcome, role, arm, field, val)
            facts.add(fact)

    return facts


# ------------------ prediction side: build arm-facts ------------------ #

def build_pred_arm_facts(jsonl_path: str):
    """
    Return a set of arm-facts from model outputs:
      (pmcid, outcome_norm, role, arm_name_norm, field, value)
    """
    pmcid = get_pmcid_from_filename(jsonl_path)
    facts = set()

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            for e in doc.get("extractions", []):
                cls = e.get("extraction_class")
                info = CLASS_INFO.get(cls)
                if info is None:
                    continue  # ignore classes not in our schema
                role, field = info

                attrs = e.get("attributes") or {}
                outcome = normalize_name(attrs.get("Outcome"))
                if role == "I":
                    arm = normalize_name(attrs.get("Intervention"))
                else:
                    arm = normalize_name(attrs.get("Comparator"))

                if arm is None:
                    continue  # can't place this extraction on an arm

                val = normalize_value(e.get("extraction_text"))
                if val is None:
                    continue

                fact = (pmcid, outcome, role, arm, field, val)
                facts.add(fact)

    return facts


# ------------------ metrics ------------------ #

def evaluate_arm_facts(gold_facts, pred_facts):
    tp = len(gold_facts & pred_facts)
    fp = len(pred_facts - gold_facts)
    fn = len(gold_facts - pred_facts)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

def print_mismatches(gold_facts, pred_facts):
    tp = gold_facts & pred_facts
    fp = pred_facts - gold_facts   # predicted but not in gold
    fn = gold_facts - pred_facts   # in gold but not predicted

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"TP: {len(tp)}  FP: {len(fp)}  FN: {len(fn)}")

    # Helper for pretty-print
    def fmt_fact(fact):
        pmcid, outcome, role, arm, field, value = fact
        role_label = "Intervention" if role == "I" else "Comparator"
        return (
            f"PMCID={pmcid}, Outcome={outcome!r}, "
            f"{role_label}={arm!r}, field={field!r}, value={value}"
        )

    # False negatives: gold fact missing in extractions
    if fn:
        print("\n" + "=" * 80)
        print("FALSE NEGATIVES (in gold, not predicted)")
        print("=" * 80)
        for fact in sorted(fn):
            print("  ", fmt_fact(fact))

    # False positives: extracted fact not in gold
    if fp:
        print("\n" + "=" * 80)
        print("FALSE POSITIVES (extracted, not in gold)")
        print("=" * 80)
        for fact in sorted(fp):
            print("  ", fmt_fact(fact))


def evaluate_file(extraction_file: str, gold_file: str):
    pmcid = get_pmcid_from_filename(extraction_file)
    gold_facts = build_gold_arm_facts(gold_file, pmcid)
    pred_facts = build_pred_arm_facts(extraction_file)

    metrics = evaluate_arm_facts(gold_facts, pred_facts)

    print(f"PMCID: {pmcid}")
    print(f"Gold arm-facts: {len(gold_facts)}")
    print(f"Pred arm-facts: {len(pred_facts)}")
    print(f"TP: {metrics['tp']}  FP: {metrics['fp']}  FN: {metrics['fn']}")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall:    {metrics['recall']:.3f}")
    print(f"F1:        {metrics['f1']:.3f}")

    # Now print non-matches
    print_mismatches(gold_facts, pred_facts)



if __name__ == "__main__":
    extraction_path = "outputs/4132222_guided_pdf.jsonl"
    gold_path = "gold-standard/annotated_rct_dataset.json"
    evaluate_file(extraction_path, gold_path)
