# Deployment Guide

## 1) Environment

- OS: Windows/Linux/macOS
- Python: 3.10+
- CPU-only runtime
- No network required during ranking step

## 2) Install

```bash
python -m pip install -r requirements.txt
```

## 3) Generate ranking output

```bash
python -m src.main rank \
  --candidates "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" \
  --out outputs/submission.csv \
  --top-k 100
```

## 4) Validate output

```bash
python "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" outputs/submission.csv
```

Expected success output:
`Submission is valid.`

## 5) Test suite

```bash
python -m pytest -q
```

## 6) Sandbox deployment options

Recommended:
- Streamlit Cloud
- HuggingFace Spaces
- Replit

For sandbox, wrap CLI in a minimal upload + run UI for <=100 candidates sample.
