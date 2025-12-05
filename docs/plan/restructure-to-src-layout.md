# Project Restructuring Plan: Migrate to src/ Layout

## Overview

This document outlines the plan to restructure the project from its current flat layout to a proper Python `src/` layout with installable packages.

## Current State Analysis

### Problems with Current Structure

1. **Placeholder `main.py`** - Auto-generated file that does nothing useful
2. **No proper package structure** - Code in `reverie/backend_server/` is not importable
3. **Extensive `sys.path` hacking** - 17 files use `sys.path.append()` for imports
4. **Hardcoded relative paths** - 5+ paths like `../../environment/frontend_server/...`
5. **Duplicate `global_methods.py`** - Three copies in different locations
6. **Tests require path injection** - `sys.path.insert(0, 'reverie/backend_server')`

### Current Directory Structure

```
modern-stanford-agents-base/
├── main.py                          # USELESS - placeholder
├── reverie/
│   ├── backend_server/              # NOT a package (no __init__.py)
│   │   ├── reverie.py              # Entry point (must run from this dir)
│   │   ├── config.py
│   │   ├── utils.py                # HARDCODED PATHS
│   │   ├── maze.py
│   │   ├── global_methods.py
│   │   └── persona/
│   │       ├── persona.py          # sys.path.append('../')
│   │       ├── cognitive_modules/  # All use sys.path.append('../../')
│   │       ├── memory_structures/  # All use sys.path.append('../../')
│   │       └── prompt_template/    # Mixed sys.path usage
│   ├── global_methods.py           # DUPLICATE
│   └── compress_sim_storage.py
├── environment/
│   └── frontend_server/             # Django app
│       ├── manage.py
│       ├── global_methods.py        # DUPLICATE
│       └── ...
├── tests/
│   ├── test_integration.py         # sys.path.insert() hacks
│   └── test_model_config.py        # sys.path.insert() hacks
└── pyproject.toml                   # No entry points defined
```

### Files with `sys.path` Manipulation (17 total)

| Location | Pattern |
|----------|---------|
| `persona/cognitive_modules/*.py` (6 files) | `sys.path.append('../../')` |
| `persona/memory_structures/*.py` (3 files) | `sys.path.append('../../')` |
| `persona/prompt_template/*.py` (3 files) | `sys.path.append('../../')` or `('../')` |
| `persona/persona.py` | `sys.path.append('../')` |
| `tests/test_*.py` (2 files) | `sys.path.insert(0, 'reverie/backend_server')` |

### Hardcoded Paths in `utils.py`

```python
maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"
fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"
```

---

## Target State

### Proposed Directory Structure

```
modern-stanford-agents-base/
├── src/
│   └── generative_agents/           # Main installable package
│       ├── __init__.py
│       ├── backend/                 # Renamed from reverie/backend_server
│       │   ├── __init__.py
│       │   ├── server.py           # Renamed from reverie.py
│       │   ├── config.py
│       │   ├── utils.py            # Updated with pathlib
│       │   ├── maze.py
│       │   ├── path_finder.py
│       │   ├── global_methods.py   # Single source of truth
│       │   └── persona/
│       │       ├── __init__.py
│       │       ├── persona.py
│       │       ├── cognitive_modules/
│       │       │   ├── __init__.py
│       │       │   ├── perceive.py
│       │       │   ├── retrieve.py
│       │       │   ├── plan.py
│       │       │   ├── reflect.py
│       │       │   ├── execute.py
│       │       │   └── converse.py
│       │       ├── memory_structures/
│       │       │   ├── __init__.py
│       │       │   ├── associative_memory.py
│       │       │   ├── spatial_memory.py
│       │       │   └── scratch.py
│       │       └── prompt_template/
│       │           ├── __init__.py
│       │           ├── gpt_structure.py
│       │           └── run_gpt_prompt.py
│       └── compress.py             # Renamed from compress_sim_storage.py
├── environment/                     # Keep Django separate (not in src/)
│   └── frontend_server/
│       ├── manage.py
│       ├── frontend_server/
│       │   ├── settings/
│       │   └── ...
│       └── translator/
├── tests/
│   ├── __init__.py
│   ├── test_integration.py
│   └── test_model_config.py
├── pyproject.toml                   # Updated with entry points
└── ...
```

### Key Changes

1. **Delete `main.py`** - Useless placeholder
2. **Create `src/generative_agents/`** - Proper installable package
3. **Consolidate `global_methods.py`** - Single copy in backend
4. **Remove all `sys.path` hacks** - Use absolute imports
5. **Convert paths to `pathlib`** - Dynamic path resolution
6. **Add `pyproject.toml` entry points** - CLI commands
7. **Keep Django in `environment/`** - Separate concern, different runtime

---

## Implementation Steps

### Phase 1: Preparation

#### Step 1.1: Delete Useless Files

- [ ] Delete `main.py` (placeholder with no functionality)
- [ ] Delete `reverie/backend_server/test.py` if it's unused
- [ ] Delete `persona/prompt_template/defunct_run_gpt_prompt.py` if deprecated

#### Step 1.2: Audit Star Imports

Document what each `from module import *` actually uses:

- [ ] Audit `global_methods.py` exports
- [ ] Audit `utils.py` exports
- [ ] Consider converting to explicit imports (optional, but cleaner)

---

### Phase 2: Create Package Structure

#### Step 2.1: Create Directory Structure

```bash
mkdir -p src/generative_agents/backend/persona/{cognitive_modules,memory_structures,prompt_template}
```

#### Step 2.2: Create `__init__.py` Files

Create `__init__.py` in each directory:

- [ ] `src/generative_agents/__init__.py`
- [ ] `src/generative_agents/backend/__init__.py`
- [ ] `src/generative_agents/backend/persona/__init__.py`
- [ ] `src/generative_agents/backend/persona/cognitive_modules/__init__.py`
- [ ] `src/generative_agents/backend/persona/memory_structures/__init__.py`
- [ ] `src/generative_agents/backend/persona/prompt_template/__init__.py`

#### Step 2.3: Move Files

| Source | Destination |
|--------|-------------|
| `reverie/backend_server/config.py` | `src/generative_agents/backend/config.py` |
| `reverie/backend_server/utils.py` | `src/generative_agents/backend/utils.py` |
| `reverie/backend_server/global_methods.py` | `src/generative_agents/backend/global_methods.py` |
| `reverie/backend_server/maze.py` | `src/generative_agents/backend/maze.py` |
| `reverie/backend_server/path_finder.py` | `src/generative_agents/backend/path_finder.py` |
| `reverie/backend_server/reverie.py` | `src/generative_agents/backend/server.py` |
| `reverie/backend_server/persona/*.py` | `src/generative_agents/backend/persona/*.py` |
| `reverie/compress_sim_storage.py` | `src/generative_agents/compress.py` |

---

### Phase 3: Update Imports

#### Step 3.1: Remove `sys.path` Hacks

Remove all `sys.path.append()` calls from:

- [ ] `persona/persona.py`
- [ ] `persona/cognitive_modules/perceive.py`
- [ ] `persona/cognitive_modules/retrieve.py`
- [ ] `persona/cognitive_modules/plan.py`
- [ ] `persona/cognitive_modules/reflect.py`
- [ ] `persona/cognitive_modules/execute.py`
- [ ] `persona/cognitive_modules/converse.py`
- [ ] `persona/memory_structures/associative_memory.py`
- [ ] `persona/memory_structures/spatial_memory.py`
- [ ] `persona/memory_structures/scratch.py`
- [ ] `persona/prompt_template/run_gpt_prompt.py`
- [ ] `persona/prompt_template/print_prompt.py`

#### Step 3.2: Convert to Absolute Imports

Replace relative imports with absolute package imports:

**Before:**
```python
sys.path.append('../../')
from global_methods import *
from utils import *
from persona.prompt_template.gpt_structure import *
```

**After:**
```python
from generative_agents.backend.global_methods import *
from generative_agents.backend.utils import *
from generative_agents.backend.persona.prompt_template.gpt_structure import *
```

#### Step 3.3: Update Import Table

| Old Import | New Import |
|------------|------------|
| `from global_methods import *` | `from generative_agents.backend.global_methods import *` |
| `from utils import *` | `from generative_agents.backend.utils import *` |
| `from config import ModelConfig` | `from generative_agents.backend.config import ModelConfig` |
| `from maze import *` | `from generative_agents.backend.maze import *` |
| `from persona.persona import *` | `from generative_agents.backend.persona.persona import *` |
| `from persona.cognitive_modules.X import *` | `from generative_agents.backend.persona.cognitive_modules.X import *` |
| `from persona.memory_structures.X import *` | `from generative_agents.backend.persona.memory_structures.X import *` |
| `from persona.prompt_template.X import *` | `from generative_agents.backend.persona.prompt_template.X import *` |

---

### Phase 4: Fix Path Handling

#### Step 4.1: Update `utils.py` with Dynamic Paths

**Before:**
```python
maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
fs_storage = "../../environment/frontend_server/storage"
```

**After:**
```python
from pathlib import Path

# Find project root (contains pyproject.toml)
def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not find project root (no pyproject.toml found)")

PROJECT_ROOT = _find_project_root()
ENVIRONMENT_DIR = PROJECT_ROOT / "environment" / "frontend_server"

maze_assets_loc = ENVIRONMENT_DIR / "static_dirs" / "assets"
env_matrix = maze_assets_loc / "the_ville" / "matrix"
env_visuals = maze_assets_loc / "the_ville" / "visuals"
fs_storage = ENVIRONMENT_DIR / "storage"
fs_temp_storage = ENVIRONMENT_DIR / "temp_storage"
```

#### Step 4.2: Update Path Usage Throughout Codebase

Convert string path operations to `pathlib`:

**Before:**
```python
fork_folder = f"{fs_storage}/{self.fork_sim_code}"
json.load(open(f"{env_matrix}/maze_meta_info.json"))
```

**After:**
```python
fork_folder = fs_storage / self.fork_sim_code
json.load(open(env_matrix / "maze_meta_info.json"))
```

Files to update:
- [ ] `server.py` (was `reverie.py`)
- [ ] `maze.py`
- [ ] `compress.py`
- [ ] `spatial_memory.py` (remove hardcoded example path)

---

### Phase 5: Update Configuration

#### Step 5.1: Update `pyproject.toml`

```toml
[project]
name = "generative-agents"
version = "0.2.0"
description = "Generative Agents: Interactive Simulacra of Human Behavior"
requires-python = ">=3.14"
dependencies = [
    "openai>=1.82.0",
    "numpy>=2.2.6",
    "python-dotenv>=1.1.0",
]

[project.scripts]
generative-agents = "generative_agents.backend.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/generative_agents"]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "ruff>=0.11.12",
]
```

#### Step 5.2: Add Entry Point Function

Create `main()` function in `server.py`:

```python
def main():
    """Entry point for the generative-agents CLI."""
    rs = ReverieServer(
        fork_sim_code=input("Enter the name of the forked simulation: ").strip(),
        sim_code=input("Enter the name for the new simulation: ").strip()
    )
    rs.start_server()

if __name__ == "__main__":
    main()
```

---

### Phase 6: Update Tests

#### Step 6.1: Remove `sys.path` Hacks from Tests

**Before:**
```python
sys.path.insert(0, 'reverie/backend_server')
sys.path.insert(0, 'reverie/backend_server/persona/prompt_template')
from config import ModelConfig
from gpt_structure import ChatGPT_request
```

**After:**
```python
from generative_agents.backend.config import ModelConfig
from generative_agents.backend.persona.prompt_template.gpt_structure import ChatGPT_request
```

#### Step 6.2: Update Test Files

- [ ] `tests/test_integration.py`
- [ ] `tests/test_model_config.py`

---

### Phase 7: Handle Django Frontend

The Django app in `environment/frontend_server/` should remain separate because:
- It has its own execution context (`manage.py`)
- It serves static files and templates
- It communicates with backend via JSON files, not imports

#### Step 7.1: Update Django `global_methods.py`

Option A: Keep Django's own copy (simpler, some duplication)
Option B: Import from installed package:

```python
# environment/frontend_server/global_methods.py
from generative_agents.backend.global_methods import *
```

#### Step 7.2: Verify Django Paths

Django settings already use dynamic paths via `BASE_DIR`. Verify these still work:
- [ ] Template paths
- [ ] Static file paths
- [ ] Database path

---

### Phase 8: Cleanup

#### Step 8.1: Remove Old Structure

After verifying everything works:

- [ ] Delete `reverie/` directory (now empty or deprecated)
- [ ] Delete duplicate `global_methods.py` files
- [ ] Delete `main.py`

#### Step 8.2: Update Documentation

- [ ] Update `README.md` with new installation/running instructions
- [ ] Update `CLAUDE.md` with new structure
- [ ] Update any other docs referencing old paths

---

## Verification Checklist

### Tests Pass

```bash
uv sync
uv run pytest -q
```

### Backend Server Runs

```bash
uv run generative-agents
# OR
uv run python -m generative_agents.backend.server
```

### Django Frontend Runs

```bash
cd environment/frontend_server
uv run python manage.py runserver
```

### Package is Installable

```bash
uv pip install -e .
python -c "from generative_agents.backend.config import ModelConfig; print('OK')"
```

---

## Risk Assessment

### High Risk Areas

1. **Import cycles** - Converting star imports may reveal circular dependencies
2. **Path resolution** - `pathlib` changes may break file operations
3. **Django integration** - May need to install package in Django's context

### Mitigation

- Run tests after each phase
- Keep old structure until new one is verified
- Use git branches for rollback capability

---

## Rollback Plan

If restructuring fails:

1. `git checkout main` to restore original structure
2. All changes are in a feature branch until verified

---

## Post-Migration Benefits

1. **Clean imports** - `from generative_agents.backend import ...`
2. **Installable package** - `uv pip install -e .`
3. **CLI entry point** - `generative-agents` command
4. **No `sys.path` hacks** - Tests work without path manipulation
5. **Type checking works** - IDEs can resolve imports
6. **Publishable** - Can upload to PyPI if desired
