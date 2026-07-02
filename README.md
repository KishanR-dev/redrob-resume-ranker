---
title: Redrob Resume Ranker
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.1
python_version: "3.10"
app_file: app.py
pinned: false
---

# Redrob Intelligent Candidate Discovery & Ranking - Production Solution

This repository contains a production-ready, deterministic ranking system for the **India Runs Data and AI Challenge**.

## Objectives covered

- Rank candidates against the provided JD (Senior AI Engineer — Founding Team).
- Output strict top-100 CSV with required schema:
  `candidate_id,rank,score,reasoning`
- Respect compute constraints for ranking step:
  CPU-only, no network, <=5 minutes expected on typical 16GB machine.
- Include anti-honeypot consistency checks.
- Provide factual, rank-consistent 1–2 sentence reasoning.
- Include tests and deployment/repro guidance.

## Project structure

- `src/data_loader.py` - streaming JSONL/JSONL.GZ loader
- `src/features.py` - JD fit, skills, experience, behavior scoring
- `src/honeypot.py` - reliability / contradiction penalties
- `src/ranker.py` - deterministic weighted ranking
- `src/reasoning.py` - factual reasoning generator
- `src/main.py` - CLI
- `tests/` - unit and integration tests
- `docs/deployment_guide.md` - deployment and execution guidance
- `submission_metadata.yaml` - metadata template filled for submission workflow

## Scoring architecture

Final score is weighted:

- JD fit: 45%
- Skills relevance: 20%
- Experience fit: 10%
- Behavioral availability: 20%
- Reliability/anti-honeypot: 5%

Tie-breaks are deterministic by `candidate_id` ascending for equal scores.

## Run ranking

```bash
python -m src.main rank \
  --candidates "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" \
  --out outputs/submission.csv \
  --top-k 100
```

## Validate submission format

```bash
python "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" outputs/submission.csv
```

## Run tests

```bash
python -m pytest -q
```

## Deploy sandbox on Hugging Face Spaces

1. Create a new Space at `https://huggingface.co/spaces`:
   - SDK: **Gradio**
   - Hardware: **CPU basic**
   - Visibility: **Public**
2. Link this GitHub repository in Space **Settings → Repository**.
3. Ensure these files are present at repo root:
   - `app.py` (Gradio UI)
   - `requirements.txt` (includes `gradio` and `pandas`)
4. Push to GitHub; Hugging Face will auto-build and deploy.

### Sandbox usage

- Open your Space URL.
- Upload `.json` or `.jsonl` candidate input.
- Click **Run Ranking**.
- Verify output columns:
  `candidate_id, rank, score, reasoning`
- Download generated CSV.

### Sandbox URL

Set your live URL in `submission_metadata.yaml` field `sandbox_link` after deployment.

## Notes on methodology

This approach intentionally avoids simple keyword stuffing traps by:
- Strong title/career-history consistency checks.
- Product-company and retrieval/ranking evidence weighting.
- Penalties for profile contradictions (e.g., salary min > max, timeline inconsistencies).
- Behavioral availability modifiers (open-to-work, recency, response patterns, notice period).

This design is interpretable, reproducible, and suitable for Stage 3–5 scrutiny.
