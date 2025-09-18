# Repository Guidelines

## Project Structure & Module Organization
- Core Python modules live in `korefi_commons/` (`filepath_generator.py`, `s3.py`, `s3uri_generator.py`, `__init__.py`). Each module is import-safe and intended for reuse across KoreFi services.
- Tests mirror the module layout in `tests/`, using one `test_*.py` per feature area for fast discovery.
- Tooling lives at the repo root: `Makefile` for dev commands, `requirements.txt` for minimal dependencies, `setup.py` for packaging, and `semver.sh` for automated version bumps.

## Environment Setup
- Target Python 3.9 to match the Bitbucket pipeline image.
- Create an isolated environment (`python -m venv .venv && source .venv/bin/activate`) and install dev deps via `make install` (editable install with extras) or `pip install -r requirements.txt` when you only need the minimal toolchain.

## Build, Test, and Development Commands
- `make install` – installs the package in editable mode plus dev requirements.
- `make test` – installs deps (if needed) then runs the canonical `pytest tests/*` suite.
- `make ruff` – installs Ruff, runs static checks (`ruff check .`), and applies formatting (`ruff format .`).
- `make coverage` – executes tests under `coverage run` and prints a coverage report; use this before pushing.

## Coding Style & Naming Conventions
- Follow Ruff defaults: 4-space indentation, 120-character max line length, and auto-formatting via `ruff format`.
- Modules and functions use `snake_case`; classes remain `PascalCase`; constants uppercase.
- Prefer explicit type hints and docstrings similar to the existing S3 services, and keep logging via module-level loggers (`logging.getLogger(__name__)`).

## Testing Guidelines
- New features require matching tests under `tests/`, named `test_<module>.py` with descriptive test functions (`test_upload_json_handles_retry`).
- Use `pytest` fixtures to mock AWS or filesystem interactions; rely on `pytest --maxfail=1` locally for quick feedback.
- Maintain or improve coverage reported by `make coverage`; call out intentional gaps in the PR description.

## Commit & Pull Request Guidelines
- Write concise, imperative commit subjects ("Add retry metadata"), optionally tagging `[skip ci]` only for version bumps handled by `semver.sh`.
- Reference related Jira or Bitbucket issues in the body, and squash noisy fixups before review.
- PRs must include: summary of changes, verification steps (`make ruff`, `make coverage`), any screenshots/logs for integration-facing work, and notes on rollout or configs.

## CI & Release Workflow
- Bitbucket Pipelines run lint and coverage checks on every pull request; keep these green to avoid auto-decline.
- Merged commits to `main` trigger `semver.sh` to increment the patch version and re-run the coverage gate—coordinate releases accordingly.
