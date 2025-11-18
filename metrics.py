import json
from pathlib import Path


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


def check_internal_inconsistencies(jsonl_path):
    """
    For each (ICO, extraction_class), count extractions and
    flag cases where more than one distinct value is present.
    """
    groups = group_by_ico_and_class(jsonl_path)

    print("=" * 80)
    print("File:", jsonl_path)
    print("Number of (ICO, class) groups:", len(groups))
    print("=" * 80)

    inconsistent_groups = []

    for (I, C, O, cls), ex_list in groups.items():
        values = [normalize_value(e.get("extraction_text")) for e in ex_list]
        # filter out None/missing
        values = [v for v in values if v is not None]
        unique_vals = sorted(set(values), key=str)

        print(f"\n--- ICO+Class ---")
        print(f"Intervention: {I}")
        print(f"Comparator:   {C}")
        print(f"Outcome:      {O}")
        print(f"Class:        {cls}")
        print(f"Num extractions: {len(ex_list)}")
        print(f"Unique normalized values: {unique_vals}")

        if len(unique_vals) > 1:
            inconsistent_groups.append(((I, C, O, cls), unique_vals))

    # Summary of inconsistencies
    print("\n" + "=" * 80)
    print("SUMMARY: POTENTIAL INCONSISTENCIES")
    print("=" * 80)
    if not inconsistent_groups:
        print("No groups with >1 distinct value.")
    else:
        for (I, C, O, cls), vals in inconsistent_groups:
            print("\n[INCONSISTENT]")
            print(f"Intervention: {I}")
            print(f"Comparator:   {C}")
            print(f"Outcome:      {O}")
            print(f"Class:        {cls}")
            print(f"Distinct values: {vals}")


# --- example usage ---
if __name__ == "__main__":
    # e.g. "5419060_guided_pdf.jsonl" or "4357072_guided_pdf.jsonl"
    extraction_file = "outputs/5419060_guided_pdf.jsonl"
    check_internal_inconsistencies(extraction_file)
