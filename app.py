from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd

from src.ranker import rank_candidates


def _load_candidates(file_path: str) -> list[dict[str, Any]]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        if path.suffix.lower() == ".jsonl":
            return [json.loads(line) for line in f if line.strip()]
        data = json.load(f)
        if isinstance(data, list):
            return data
        raise ValueError("JSON input must be a list of candidate objects")


def process(file: Any) -> tuple[pd.DataFrame | None, str | None, str]:
    if file is None:
        return None, None, "Upload a .json or .jsonl file"

    try:
        candidates = _load_candidates(file.name)
        ranked = rank_candidates(candidates, top_k=100)

        rows = [
            {
                "candidate_id": item.candidate_id,
                "rank": item.rank,
                "score": round(float(item.score), 6),
                "reasoning": item.reasoning,
            }
            for item in ranked
        ]
        df = pd.DataFrame(rows, columns=["candidate_id", "rank", "score", "reasoning"])

        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_csv_path = tmp_csv.name
        tmp_csv.close()
        df.to_csv(tmp_csv_path, index=False)

        return df, tmp_csv_path, f"Processed {len(candidates)} candidates. Returning top {len(df)}."
    except Exception as exc:  # pragma: no cover
        return None, None, f"Error: {exc}"


with gr.Blocks() as demo:
    gr.Markdown("# Redrob Ranker Sandbox")
    gr.Markdown("Upload a candidate file in `.json` or `.jsonl` format to rank and export results as CSV.")

    file_input = gr.File(label="Upload candidates file (.json or .jsonl)")
    run_btn = gr.Button("Run Ranking")

    results_table = gr.Dataframe(label="Top Ranked Candidates")
    download_file = gr.File(label="Download submission CSV")
    status_box = gr.Textbox(label="Status", interactive=False)

    run_btn.click(
        fn=process,
        inputs=file_input,
        outputs=[results_table, download_file, status_box],
    )

demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
