import json
from pathlib import Path
from math import isclose



def normalize_name(s):
    """Lowercase + collapse whitespace for text labels. Keeps None as None."""
    if s is None:
        return None
    return " ".join(s.lower().split())


def normalize_value(v):
    """
    Normalize extraction_text for consistency checking.

    - strip spaces, lowercase
    - treat '', 'none', 'nr', 'not reported', 'n/a', 'na' as missing (-> None)
    - handle percentages: '0%' and '0.0%' become the same normalized value
    - keep distinction between plain numbers and percentages:
        20   -> ('plain', 20.0)
        20%  -> ('percent', 20.0)
    - for non-numeric stuff, return the cleaned string
    """
    if v is None:
        return None

    s = str(v).strip().lower()
    if s in {"", "none", "nr", "not reported", "n/a", "na"}:
        return None

    is_percent = s.endswith("%")
    if is_percent:
        s_num = s[:-1].strip()  # drop '%'
    else:
        s_num = s

    # try numeric
    try:
        val = float(s_num)
        val = round(val, 6)  # stable comparison
        kind = "percent" if is_percent else "plain"
        return (kind, val)
    except ValueError:
        # not numeric at all, just return cleaned string
        return s



def group_by_ico_and_class(jsonl_path):
    """
    Read LangExtract .jsonl and group by:
      (Intervention, Comparator, Outcome, extraction_class)

    Returns:
      groups: dict[
        (I_norm, C_norm, O_norm, extraction_class) -> list[extraction dict]
      ]
    """
    groups = {}

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            for e in doc.get("extractions", []):
                attrs = e.get("attributes") or {}
                I = normalize_name(attrs.get("Intervention"))
                C = normalize_name(attrs.get("Comparator"))
                O = normalize_name(attrs.get("Outcome"))
                cls = e.get("extraction_class")

                # We at least need an intervention + outcome to define an ICO
                if I is None or O is None or cls is None:
                    continue

                key = (I, C, O, cls)
                groups.setdefault(key, []).append(e)

    return groups


def group_by_full_ico_and_class(jsonl_path):
    """
    Use group_by_ico_and_class, but keep only groups with a *complete* ICO:
      - Intervention, Comparator, Outcome are all present and non-empty
      (after normalization).

    Returns:
      groups: dict[
        (I_norm, C_norm, O_norm, extraction_class) -> list[extraction dict]
      ]
    """
    all_groups = group_by_ico_and_class(jsonl_path)
    full_groups = {}

    for (I, C, O, cls), ex_list in all_groups.items():
        # I and O are guaranteed non-None in group_by_ico_and_class, but may be ""
        if (
            I is None or I == "" or
            O is None or O == "" or
            C is None or C == ""
        ):
            continue

        full_groups[(I, C, O, cls)] = ex_list

    return full_groups


NUMERIC_FIELDS = [
    "intervention_events",
    "intervention_group_size",
    "comparator_events",
    "comparator_group_size",
    "intervention_mean",
    "intervention_standard_deviation",
    "comparator_mean",
    "comparator_standard_deviation",
]

# Map LangExtract extraction_class -> gold field name
FIELD_MAP = {
    # events
    "intervention_events": "intervention_events",
    "comparator_events": "comparator_events",

    # group sizes
    "intervention_group_size": "intervention_group_size",
    "comparator_group_size": "comparator_group_size",
    "intervention_groupsize": "intervention_group_size",
    "comparator_groupsize": "comparator_group_size",

    # means
    "intervention_mean": "intervention_mean",
    "mean_intervention": "intervention_mean",
    "comparator_mean": "comparator_mean",
    "mean_comparator": "comparator_mean",

    # standard deviations
    "intervention_standard_deviation": "intervention_standard_deviation",
    "sd_intervention": "intervention_standard_deviation",
    "comparator_standard_deviation": "comparator_standard_deviation",
    "sd_comparator": "comparator_standard_deviation",
}


def get_pmcid_from_filename(path):
    """
    Extract first sequence of digits from filename, e.g.
      'outputs/4357072_guided_pdf.jsonl' -> 4357072 (int)
    """
    name = Path(path).name
    digits = "".join(ch for ch in name if ch.isdigit())
    if not digits:
        raise ValueError(f"No digits (pmcid) found in filename: {name}")
    return int(digits)


def to_float_or_none(x):
    """
    Basic numeric normalisation for gold and predictions.
    Handles '', None, simple 'NR'-style cases, and strips '%' if present.
    """
    if x is None:
        return None
    s = str(x).strip().lower()
    if s in {"", "none", "nr", "not reported", "n/a", "na"}:
        return None
    if s.endswith("%"):
        s = s[:-1].strip()
    try:
        return float(s)
    except ValueError:
        return None


# ---------- GOLD SIDE ----------

def load_gold_for_pmcid(gold_json_path, pmcid):
    """
    For a given pmcid, return:
      dict[(I_norm, C_norm, O_norm)] = { field_name -> float_or_None }
    """
    with open(gold_json_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    by_ico = {}

    for row in rows:
        if int(row["pmcid"]) != int(pmcid):
            continue

        I = normalize_name(row["intervention"])
        C = normalize_name(row["comparator"])
        O = normalize_name(row["outcome"])

        if not I or not C or not O:
            continue

        key = (I, C, O)
        values = {field: to_float_or_none(row.get(field)) for field in NUMERIC_FIELDS}
        by_ico[key] = values

    return by_ico


# ---------- PREDICTION SIDE ----------

def build_pred_values_by_ico(jsonl_path):
    """
    Use group_by_ico_and_class and FIELD_MAP to get predicted numeric values.

    Returns:
      dict[(I, C, O)] = { field_name -> float_or_None }

    If multiple distinct values exist for same ICO+field, we:
      - print a note,
      - pick the first one (prototype behaviour).
    """
    groups = group_by_ico_and_class(jsonl_path)
    by_ico = {}

    for (I, C, O, cls), ex_list in groups.items():
        field = FIELD_MAP.get(cls)
        if field is None:
            continue  # ignore extraction_classes without a gold counterpart

        # lazily init
        key = (I, C, O)
        if key not in by_ico:
            by_ico[key] = {}

        # gather numeric values
        vals = {to_float_or_none(e.get("extraction_text")) for e in ex_list}
        vals = {v for v in vals if v is not None}

        if not vals:
            continue

        if len(vals) > 1:
            # prototype: warn, then pick arbitrary one
            print(
                f"[WARN] Multiple values for ICO={key}, field={field}: {sorted(vals)} "
                f"(picking the first for comparison)"
            )

        by_ico[key][field] = sorted(vals)[0]

    return by_ico


# ---------- COMPARISON ----------

def compare_values_for_pmcid(extraction_file, gold_json_path, tol=1e-3):
    """
    Prototype: for one PMCID, compare extracted numeric values against gold, per ICO.

    For each gold ICO:
      - look up predicted values for that ICO
      - compare each numeric field (when gold is present)
      - print gold vs pred and whether they match
    """
    pmcid = get_pmcid_from_filename(extraction_file)
    gold_by_ico = load_gold_for_pmcid(gold_json_path, pmcid)
    pred_by_ico = build_pred_values_by_ico(extraction_file)

    print("=" * 80)
    print(f"PMCID {pmcid} – ICO VALUE COMPARISON")
    print("=" * 80)

    total_fields = 0
    matched = 0
    missing_pred = 0
    mismatched = 0

    for ico_key, gold_vals in gold_by_ico.items():
        I, C, O = ico_key
        pred_vals = pred_by_ico.get(ico_key, {})

        print("\n--- ICO ---")
        print(f"Intervention: {I}")
        print(f"Comparator:   {C}")
        print(f"Outcome:      {O}")

        for field in NUMERIC_FIELDS:
            g = gold_vals.get(field)
            if g is None:
                continue  # no gold value to compare

            total_fields += 1
            p = pred_vals.get(field)

            if p is None:
                status = "MISSING_PRED"
                missing_pred += 1
            else:
                if isclose(g, p, rel_tol=tol, abs_tol=tol):
                    status = "MATCH"
                    matched += 1
                else:
                    status = "MISMATCH"
                    mismatched += 1

            print(f"  {field}: gold={g}, pred={p} -> {status}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total gold numeric values (across ICOs): {total_fields}")
    print(f"Matched:      {matched}")
    print(f"Missing pred: {missing_pred}")
    print(f"Mismatched:   {mismatched}")
    if total_fields:
        print(f"Match rate:   {matched / total_fields:.3f}")


# --- example usage ---
if __name__ == "__main__":
    extraction_file = "outputs/5419060_guided_pdf.jsonl"
    gold_path = "gold-standard/annotated_rct_dataset.json"
    compare_values_for_pmcid(extraction_file, gold_path)