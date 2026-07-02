from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


def sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text.strip())
    return len([p for p in parts if p.strip()])


def has_truncated_fragment(text: str) -> bool:
    # catch suspicious standalone fragments often caused by bad slicing
    bad_patterns = [
        r"\bwhere they [a-z]{1,4}\b",
        r"\b(?:ative|ment|th)\b\.",
        r"\b[a-z]{1,3}\.\s*$",
    ]
    low = text.lower()
    return any(re.search(p, low) for p in bad_patterns)


def opener_bucket(text: str) -> str:
    low = text.lower()
    if low.startswith("career evidence points to"):
        return "career evidence points to"
    if low.startswith("role history highlights"):
        return "role history highlights"
    if low.startswith("past delivery shows"):
        return "past delivery shows"
    if low.startswith("experience includes"):
        return "experience includes"
    if low.startswith("available history shows"):
        return "available history shows"
    if low.startswith("the profile indicates"):
        return "the profile indicates"
    if low.startswith("observed career signals suggest"):
        return "observed career signals suggest"
    if low.startswith("current evidence shows"):
        return "current evidence shows"
    return "other"


def main() -> None:
    submission = Path("outputs/submission.csv")
    if not submission.exists():
        raise FileNotFoundError("outputs/submission.csv not found")

    rows = []
    with submission.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    reasonings = [r.get("reasoning", "") for r in rows]
    total = len(reasonings)
    unique = len(set(reasonings))
    opener_counts = Counter(opener_bucket(r) for r in reasonings)

    sent_violations = [r for r in reasonings if sentence_count(r) not in {1, 2}]
    trunc_hits = [r for r in reasonings if has_truncated_fragment(r)]

    print(f"rows={total}")
    print(f"unique_reasonings={unique}")
    print(f"uniqueness_ratio={unique / total if total else 0:.4f}")
    print(f"sentence_count_violations={len(sent_violations)}")
    print(f"truncated_fragment_hits={len(trunc_hits)}")
    print("opener_distribution_top:")
    for k, v in opener_counts.most_common():
        print(f"  {k}: {v}")

    if sent_violations:
        print("\nSample sentence_count_violations:")
        for s in sent_violations[:5]:
            print(f"- {s[:220]}")

    if trunc_hits:
        print("\nSample truncated_fragment_hits:")
        for s in trunc_hits[:5]:
            print(f"- {s[:220]}")


if __name__ == "__main__":
    main()
