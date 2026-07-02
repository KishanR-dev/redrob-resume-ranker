# Ranking System Rewrite TODO

- [x] Rebalance scoring weights in `src/config.py` (behavior 0.18-0.20, slight jd/title bump, skills <= 0.03)
- [x] Strengthen `jd_fit_score` in `src/features.py` with deep production/eval/ownership/impact parsing from `career_history`
- [x] Tighten `behavior_score` long-notice (>90 days) handling when other signals are only average
- [x] Replace `src/reasoning.py` with varied 1-2 sentence evidence-based reasoning using concrete career facts
- [x] Ensure reasoning reflects deeper jd_fit evidence and behavioral assessment without templates
- [x] Update tests in `tests/test_honeypot_and_reasoning.py` for new reasoning behavior
- [x] Update/add tests in `tests/test_features.py` for strengthened jd_fit behavior
- [x] Add Hugging Face Spaces Gradio app (`app.py`) for JSON/JSONL upload and CSV export
- [x] Update `requirements.txt` with sandbox dependencies (`gradio`, `pandas`)
- [x] Update `README.md` with sandbox deployment and GitHub linking steps
- [ ] Run quick local validation for app/module imports
- [ ] Run full test suite
- [ ] Regenerate `outputs/submission.csv` from full candidates file
- [ ] Run submission validation script
