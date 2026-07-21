# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project

A small collection of Starlette-compatible middleware (FastAPI-compatible), distributed as `starlette-middleware-collection` on PyPI. Requires Python 3.14+ only (relies on `uuid.uuid7`, PEP 604 unions, etc.) — do not add compatibility shims for older Python versions.

## Commands

This project uses [uv](https://astral.sh/uv) for dependency management, [ruff](https://astral.sh/ruff) for lint/format, and [ty](https://github.com/astral-sh/ty) for type checking.

```bash
uv sync --all-groups  # install project + dev dependencies
uv run pytest -q  # run full test suite
uv run pytest tests/<some_file.py> -q  # run a single test file
uv run pytest tests/<some_file.py>::<test_name> -q  # run a single test
uv tool run ruff check  # lint
uv tool run ruff check --fix  # lint with autofix
uv tool run ruff format  # format
uv tool run ty check  # type check
uv build  # build sdist/wheel into dist/
```

Pre-commit hooks (via [prek](https://prek.j178.dev/)) run `uv-lock`, `ruff-check --fix`, `ruff-format`, `ty check`, and `pytest --maxfail=1` on commit — see `.pre-commit-config.yaml`. CI (`.github/workflows/ci-publish.yml`) runs ruff, ty, and pytest on every PR/push, and publishes to PyPI on `v*` tags after CI passes.

## Architecture

Each middleware lives in its own module under `src/starlette_middleware_collection/` and is re-exported from `__init__.py`. All middleware follow the same pattern, established by `size_limit.py` and `request_uuid.py`:

- Subclass `starlette.middleware.base.BaseHTTPMiddleware`.
- `__init__` accepts an optional constructor argument (e.g. `limit`, `uuid_version`) that, when omitted, falls back to a module-level `ENV_VAR_NAME` environment variable, then to a hardcoded default. **Constructor argument always takes precedence over the environment variable.**
- Behavior is implemented in `async def dispatch(self, request, call_next)`.
- Each module defines its own `ENV_VAR_NAME` constant (e.g. `MW_REQUEST_BODY_LIMIT`, `MW_UUID_VERSION`) — these are read at middleware init time, not at import time, so tests can set/unset `os.environ` per-test.

When adding a new middleware, follow this same shape (module-level `ENV_VAR_NAME`, constructor-arg-over-env-var precedence, dispatch-based logic) and export it from `__init__.py` and `__all__`. Shared logic is factored into helpers rather than duplicated.

### Tests

Tests use FastAPI's `TestClient` against a minimal app built in a local `setup_app()` helper per test file, mirroring the constructor-arg vs. env-var precedence rules of the middleware under test (see `tests/test_size_limit.py` and `tests/test_request_uuid.py` for the pattern to replicate for new middleware).

## Release / Publish

When releasing a new version:

- Bump versions using `uv version --bump patch` for small fixes or `uv version --bump minor` for larger API changes or new features. Do not bump major versions. Do not edit `pyproject.toml` or `uv.lock` directly.
- Use `git tag vX.X.X` and `git push origin main --tags` and the CI job will do the publish to PYPI.
