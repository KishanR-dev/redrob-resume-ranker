from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .data_loader import iter_candidates
from .ranker import rank_candidates


def run_rank(candidates_path: str, out_csv: str, top_k: int) -> None:
    candidates = list(iter_candidates(candidates_path))
    top = rank_candidates(candidates, top_k=top_k)

    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "rank", "score", "reasoning"])
        prev_score = None
        prev_candidate_id = ""
        for row in top:
            score_value = row.score
            if prev_score is not None and score_value > prev_score:
                score_value = prev_score
            if prev_score is not None and abs(score_value - prev_score) < 1e-12:
                if row.candidate_id < prev_candidate_id:
                    score_value = prev_score - 1e-6
            w.writerow([row.candidate_id, row.rank, f"{score_value:.6f}", row.reasoning])
            prev_score = score_value
            prev_candidate_id = row.candidate_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Redrob challenge ranker")
    sub = parser.add_subparsers(dest="command", required=True)

    rank_cmd = sub.add_parser("rank", help="Rank candidates and produce submission CSV")
    rank_cmd.add_argument("--candidates", required=True, help="Path to candidates.jsonl or .jsonl.gz")
    rank_cmd.add_argument("--out", required=True, help="Output CSV path")
    rank_cmd.add_argument("--top-k", type=int, default=100, help="Number of candidates to output")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "rank":
        run_rank(args.candidates, args.out, args.top_k)


if __name__ == "__main__":
    main()
