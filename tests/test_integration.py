import csv
import subprocess
import sys
from pathlib import Path


def test_end_to_end_submission_generation():
    out = Path("outputs/test_submission.csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "src.main",
        "rank",
        "--candidates",
        "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl",
        "--out",
        str(out),
        "--top-k",
        "100",
    ]
    subprocess.run(cmd, check=True)

    with open(out, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["candidate_id", "rank", "score", "reasoning"]
    assert len(rows) == 101
