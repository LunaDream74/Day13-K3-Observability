# Repository Guidelines

## Project Structure & Module Organization

`app/` contains the FastAPI service, mock RAG/LLM components, structured logging, metrics, tracing, prompt management, and PII handling. Keep HTTP concerns in `app/main.py` and reusable behavior in focused modules. `tests/` holds pytest coverage, with filenames matching `test_*.py`. Operational utilities live in `scripts/`; run them from the repository root so relative paths resolve correctly. Configuration contracts are under `config/`, sample inputs are under `data/`, and lab instructions and dashboard documentation are under `docs/`. Put submission notes and evidence in `submission/` as described in `SUBMISSION.md`.

## Build, Test, and Development Commands

Create and activate a virtual environment, then install pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

- `uvicorn app.main:app --reload --env-file .env` starts the local API.
- `python -m pytest -q` runs the complete test suite.
- `python scripts/load_test.py` generates traffic and `data/logs.jsonl`.
- `python scripts/validate_logs.py` checks the logging and PII contract.
- `python scripts/validate_dashboard.py` verifies all six dashboard panels.
- `python scripts/inject_incident.py --scenario rag_slow` enables the safe practice incident.

## Coding Style & Naming Conventions

Use Python 3 type hints, four-space indentation, and PEP 8 naming: `snake_case` for modules, functions, and variables; `PascalCase` for classes; and uppercase names for constants. Keep imports grouped as standard library, third-party, then local modules. Prefer small, single-purpose functions and explicit return types. No formatter or linter is configured, so match surrounding code and review diffs for consistency.

## Testing Guidelines

Write pytest tests beside related coverage in `tests/`. Name tests descriptively, for example `test_validator_rejects_panel_without_threshold`. Use `monkeypatch` for environment or dependency isolation and `tmp_path` for generated logs/configuration; do not write runtime artifacts into tracked fixtures. Add regression coverage for bug fixes, especially PII redaction, correlation IDs, prompt metadata, and dashboard contracts. Run the full suite and relevant validators before submitting.

## Commit & Pull Request Guidelines

History uses concise Conventional Commit subjects such as `feat: add dashboard workflow` and `fix: detect Vietnamese phone PII`. Keep each commit focused. Pull requests should explain the behavior changed, list verification commands, link the relevant issue or checkpoint, and include screenshots or trace/log IDs when observability output changes. Never commit `.env`, credentials, raw PII, generated logs, or fabricated evidence. Do not create, edit, or replace `config/challenge.json`; official challenge configuration is coach-managed.
