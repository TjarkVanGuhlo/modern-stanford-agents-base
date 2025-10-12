Project development guidelines (advanced)

This document captures project-specific knowledge to speed up future development and debugging. It is meant for experienced developers familiar with Python, uv, pytest, Django, and mocking external APIs.

1) Build and configuration

- Python and toolchain
  - Python: requires >= 3.14 (pyproject). uv will create a local virtual environment automatically.
  - Tooling: use uv for all dependency and execution tasks to ensure consistent resolution against latest versions within the specified ranges.

- Initial setup
  - Sync dependencies (creates .venv):
    - uv sync
  - Run any command inside the environment:
    - uv run <cmd>
  - Useful uv notes:
    - Add runtime (prod) dependency: uv add <pkg>
    - Add dev dependency (e.g., test tools): uv add --group dev <pkg>
    - Update lock and refresh env: uv sync

- Environment variables
  - Minimal required for model calls and ownership tagging (see README):
    - OPENAI_API_KEY
    - KEY_OWNER
  - Model selection is configured via the backend config module (reverie/backend_server/config.py) and can be controlled by environment variables at process start:
    - MODEL_PRESET ∈ {performance, balanced, economy}
    - Individual overrides (take precedence over preset):
      - MODEL_PERCEIVE
      - MODEL_RETRIEVE_EMBEDDING
      - MODEL_PLAN
      - MODEL_REFLECT
      - MODEL_EXECUTE
      - MODEL_CONVERSE
  - Important: Changes to MODEL_PRESET or individual overrides are read on import; if you change them, restart the process or reload modules during tests (see Testing section for guidance).

- Running the servers (simulation)
  - Frontend environment server (Django):
    - cd environment/frontend_server
    - uv run python manage.py runserver
    - Visit http://localhost:8000/ to verify it’s up.
  - Backend simulation server:
    - cd reverie/backend_server
    - uv run python reverie.py
    - Follow prompts to load a base simulation (e.g., base_the_ville_isabella_maria_klaus) and name your run.

- Storage conventions (from README)
  - Saved simulations: environment/frontend_server/storage
  - Compressed demo simulations: environment/frontend_server/compressed_storage

2) Testing

- Framework and runner
  - Tests use pytest (declared in dependency group dev). Always run via uv:
    - Run full suite: uv run pytest -q
    - Single file: uv run pytest tests/test_integration.py -q
    - By keyword: uv run pytest -k "model_config and not integration" -q
    - Show stdout on failure: add -rP or -v for verbose.

- Project-specific import context used in tests
  - Several tests prepend search paths so they can import backend modules directly:
    - sys.path.insert(0, 'reverie/backend_server')
    - sys.path.insert(0, 'reverie/backend_server/persona/prompt_template')
  - If you add tests that import config, utils, or gpt_structure, follow the same pattern unless you package these modules. Keep imports side-effect-free where possible.

- Environment variable driven config
  - Many tests verify that configuration is read at import time. When testing different presets within a single pytest run, you must ensure a clean import boundary.
  - Pattern used in tests:
    - Manipulate environment via patch.dict(os.environ, {...}, clear=...) or set/unset os.environ keys.
    - Ensure a fresh import by clearing affected modules from sys.modules before re-importing. Example modules to clear: ['config', 'utils', 'gpt_structure'].
    - Some tests provide fixtures for this (e.g., clean_imports in tests/test_integration.py).

- Mocking OpenAI calls
  - Real OpenAI calls must not run during tests. Tests patch gpt_structure.client and provide MagicMock responses for chat completions and embeddings. Follow that approach for any new functionality touching OpenAI.

- Adding a new test (validated example)
  - Example content for a simple smoke test that asserts default and env-override behavior (we verified this locally end-to-end):
    - Create tests/test_smoke_temp.py with:
      - import os, sys
      - sys.path.insert(0, 'reverie/backend_server')
      - from config import ModelConfig
      - assert ModelConfig().PLAN == 'gpt-4o'
      - Set os.environ['MODEL_PRESET'] = 'economy'; then assert ModelConfig.from_env().PLAN == 'gpt-4o-mini'; clean up env
    - Run it:
      - uv run pytest -q tests/test_smoke_temp.py
    - Remove it after use to avoid clutter.

- Useful pytest tips for this repo
  - Keep tests independent of a running Django server; tests interact with backend config and gpt_structure only.
  - If a test relies on env defaults, explicitly set OPENAI_API_KEY and KEY_OWNER with patch.dict to avoid dependency on host environment.

3) Additional development information

- Code organization (backend excerpts)
  - reverie/backend_server/config.py provides ModelConfig, presets, from_env(), module-level model_config, and constants consumed by other modules.
  - reverie/backend_server/utils.py consumes configured models for various helper routines (see tests referencing utils imports and backward compatibility).
  - reverie/backend_server/gpt_structure.py defines ChatGPT_request, GPT4_request, get_embedding and binds them to the configured model constants (MODEL_PLAN, MODEL_REFLECT, MODEL_RETRIEVE_EMBEDDING). All network calls should be centralized here and mocked in tests.

- Runtime model selection contract (as enforced by tests)
  - Presets:
    - performance: all gpt-4o for chat; embeddings set to text-embedding-3-large.
    - balanced (default): mix of gpt-4o and gpt-4o-mini; embeddings large.
    - economy: mostly gpt-4o-mini; embeddings text-embedding-3-small; reflection remains gpt-4o to keep quality.
  - from_env() must raise ValueError on unknown preset; individual overrides via env take precedence over preset.

- Style and versions
  - Use modern Python 3.13+ features where appropriate (pattern matching, typing, contextlib). Prefer explicit type hints for public functions/classes.
  - The project intentionally targets the latest library versions within open upper bounds (>= constraints in pyproject). Avoid pinning exact versions unless required to fix a regression; prefer bumping minimum versions and relying on uv’s resolution.

- Dependency hygiene
  - Runtime deps in [project].dependencies; test/dev-only deps in [dependency-groups].dev.
  - Use uv add and uv sync instead of editing the lock by hand. Always validate with uv run pytest before pushing changes.

- Debugging tips
  - When changing config import-time behavior, write tests that clear sys.modules and assert both default and env-controlled paths.
  - If you observe flaky behavior due to rate limits or external APIs, ensure all such calls are behind easily mockable facades (as in gpt_structure).
  - For Django UI during development: prefer running with an isolated .env and separate terminal windows; don’t interleave server runs and tests in one process.

- Running end-to-end locally (manual)
  - Ensure .env in project root contains:
    - OPENAI_API_KEY=...
    - KEY_OWNER=...
    - Optionally MODEL_PRESET=balanced|performance|economy and/or individual overrides listed above.
  - Start environment server and simulation server as described in Build and configuration.

- Clean repository policy for examples
  - Any ad hoc example tests or scripts used for demonstration should be deleted after verification. Only persistent documentation should be added under .junie/.

4) Versioning and releases

- Tag style used in this repo
  - Git tags use a leading "v" followed by semver version numbers. Examples: v0.1.8, v0.1.9, v0.1.10.
  - Always keep tags and pyproject version in sync (version in pyproject.toml must match the release tag).

- When to bump
  - Patch (x.y.Z): documentation-only changes, internal refactors, minor fixes, CI/docs/guidelines updates.
  - Minor (x.Y.z): backward-compatible features or improvements across the codebase.
  - Major (X.y.z): breaking changes to runtime behavior or public APIs.

- How to bump and release (using uv, git, and gh)
  1. Update version in pyproject.toml (project.version) to the new value (e.g., 0.1.10). Ensure Python >=3.14 compatibility remains unchanged.  
  2. Run tests locally to validate: `uv sync && uv run pytest -q`.  
  3. Commit all modified files together (don’t forget docs like README.md and .junie/guidelines.md when they change):  
     - `git add -A`  
     - `git commit -m "chore(release): bump version to 0.1.10"`  
  4. Create an annotated tag using the repo’s tag style (leading v):  
     - `git tag -a v0.1.10 -m "Release v0.1.10"`  
  5. Push branch and tags:  
     - `git push`  
     - `git push --tags`  
  6. Create a GitHub release for the tag with gh (requires workflow scope; see TJARK_SETUP.md):  
     - `gh release create v0.1.10 --title "v0.1.10" --notes "<highlights of changes>"`  

- Notes
  - The GitHub tag must match the version in pyproject.toml exactly, prefixed with "v".  
  - See TJARK_SETUP.md for GitHub CLI multi-account setup and required scopes (repo, workflow).  
  - If tests depend on environment defaults, set OPENAI_API_KEY and KEY_OWNER via patch.dict during tests or in a local .env when running servers.
