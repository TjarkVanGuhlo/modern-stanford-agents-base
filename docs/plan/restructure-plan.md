# Project Restructure Plan

This document outlines the comprehensive plan to restructure the modern-stanford-agents-base project following Python best practices. The plan is organized into phases with clear dependencies and priorities.

## Executive Summary

The project requires structural improvements in four key areas:
1. **Security** - Critical Django vulnerabilities need immediate attention
2. **Structure** - Directory layout needs clarification and simplification
3. **Code Quality** - Technical debt and maintenance issues
4. **Testing** - Comprehensive test coverage is missing

## Current Issues Overview

| Phase | Issues | Priority |
|-------|--------|----------|
| Security | ~~#59~~, #60, #61 | Critical |
| Structure | #62, #63, #64, #65 | High |
| Code Quality | #66, #67, #68, #69, #76, #77, #78 | Medium |
| Testing | #70, #71, #72, #73 | Medium |

Note: #59 has been completed.

---

## Phase 1: Security (Critical)

These issues must be resolved before any deployment or public access.

### #59 - Fix Django Security Vulnerabilities in Settings

**Priority:** Critical
**Effort:** Low
**Risk:** High if not addressed

**Problems:**
- Hardcoded `SECRET_KEY` in `settings/base.py:23`
- CSRF protection disabled (`settings/base.py:48`)
- `DEBUG = True` always enabled
- `ALLOWED_HOSTS = []` accepts any host

**Actions:**
1. Load `SECRET_KEY` from environment variable
2. Enable CSRF middleware
3. Control `DEBUG` via environment variable (default: False)
4. Configure `ALLOWED_HOSTS` via environment variable

### #60 - Add Input Validation to Django POST Endpoints

**Priority:** Critical
**Effort:** Medium
**Risk:** Path traversal and arbitrary file write vulnerabilities

**Affected Endpoints:**
- `process_environment()` - writes to user-controlled paths
- `path_tester_update()` - writes without validation
- `update_environment()` - reads from user-controlled paths

**Actions:**
1. Create `validate_sim_code()` function with allowlist pattern
2. Create `safe_storage_path()` function preventing path traversal
3. Validate `step` is a non-negative integer
4. Return HTTP 400 for invalid requests

### #61 - Remove Legacy runtime.txt File

**Priority:** Low
**Effort:** Minimal
**Risk:** None

**Problem:** `runtime.txt` specifies Python 3.9.12, conflicts with `pyproject.toml` requirement of >=3.14.2

**Actions:**
1. Delete `environment/frontend_server/runtime.txt`
2. Delete `environment/frontend_server/Procfile` if unused

---

## Phase 2: Structure (High Priority)

These changes establish the foundation for long-term maintainability.

### #62 - Restructure Project: Rename environment/ to web/

**Priority:** High
**Effort:** Medium
**Dependencies:** None
**Blocking:** #63, #64, #65

**Current Structure:**
```
environment/
└── frontend_server/
    ├── frontend_server/    # Confusing double nesting
    │   └── settings/
    ├── translator/
    └── ...
```

**Target Structure:**
```
web/
├── config/                 # Was: frontend_server/frontend_server/
│   └── settings/
├── api/                    # Was: translator/
├── templates/
└── static/
```

**Actions:**
1. Create `web/` directory
2. Move and rename subdirectories
3. Update Django settings (ROOT_URLCONF, WSGI_APPLICATION)
4. Update backend `utils.py` path references
5. Update documentation

### #63 - Move Data Directories to Project Root

**Priority:** High
**Effort:** Medium
**Dependencies:** #62

**Current Structure:**
```
environment/frontend_server/
├── storage/              # 17,000+ files per simulation
├── compressed_storage/
├── temp_storage/
└── static_dirs/assets/
```

**Target Structure:**
```
project-root/
├── data/
│   ├── simulations/      # Was: storage/
│   ├── compressed/       # Was: compressed_storage/
│   └── temp/             # Was: temp_storage/
└── assets/               # Was: static_dirs/assets/
```

**Benefits:**
- Clear separation of code vs data
- Smaller web directory (code only)
- Easier gitignore management
- Better IDE performance

### #64 - Remove Duplicate global_methods.py Files

**Priority:** Medium
**Effort:** Low
**Dependencies:** #62, #63

**Problem:** Two nearly identical files exist:
- `src/generative_agents/backend/global_methods.py` (240 lines)
- `environment/frontend_server/global_methods.py` (227 lines)

**Actions:**
1. Merge best practices into backend version
2. Delete frontend version
3. Update frontend imports to use backend package

### #65 - Add Environment Variable Support for Storage Paths

**Priority:** Medium
**Effort:** Low
**Dependencies:** #63

**Current:** All paths hardcoded in `utils.py`

**Target:** Environment variable overrides with sensible defaults:
```python
DATA_DIR = Path(os.getenv("GENERATIVE_AGENTS_DATA_DIR", PROJECT_ROOT / "data"))
ASSETS_DIR = Path(os.getenv("GENERATIVE_AGENTS_ASSETS_DIR", PROJECT_ROOT / "assets"))
```

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `GENERATIVE_AGENTS_DATA_DIR` | `{PROJECT_ROOT}/data` | Simulation data |
| `GENERATIVE_AGENTS_ASSETS_DIR` | `{PROJECT_ROOT}/assets` | Game assets |
| `GENERATIVE_AGENTS_WEB_DIR` | `{PROJECT_ROOT}/web` | Django frontend |

---

## Phase 3: Code Quality (Medium Priority)

These changes improve maintainability and developer experience.

### #76 - Extract CLI Command Handlers from server.py to Commands Module

**Priority:** High (within phase)
**Effort:** Medium
**Dependencies:** None

**Problem:** The `open_server()` method in `server.py` contains a 197-line if/elif chain with 17 different command handlers.

**Current State:**
- Method spans lines 425-609 (197 lines)
- 17 different command patterns handled via if/elif chain
- Commands include: run, save, fin, exit, print persona schedule, print tile event, call -- analysis, etc.

**Target Structure:**
```
src/generative_agents/backend/
├── server.py              # Slim ReverieServer class
└── commands/
    ├── __init__.py        # Command registry and dispatcher
    ├── simulation.py      # run, save, fin, exit commands
    ├── inspection.py      # print commands (persona, tile, time)
    └── tools.py           # call -- commands (analysis, load history)
```

**Benefits:**
- Each command handler isolated and testable
- Adding new commands doesn't require modifying giant if/elif chain
- Command registry can auto-generate help text
- `open_server()` reduced to < 50 lines

### #77 - Extract Path Tester to Separate Utility Module

**Priority:** Medium
**Effort:** Low
**Dependencies:** None

**Problem:** `start_path_tester_server()` is a 96-line self-contained utility rarely used outside of map development.

**Target Structure:**
```
src/generative_agents/backend/
├── server.py              # ReverieServer without path tester
└── tools/
    ├── __init__.py
    └── path_tester.py     # Standalone path tester
```

### #78 - Refactor ReverieServer.__init__ with Helper Methods

**Priority:** Low
**Effort:** Low
**Dependencies:** None

**Problem:** `__init__()` is 111 lines with multiple logical sections that could be clearer with helper methods.

**Proposed Helper Methods:**
- `_setup_simulation_fork()` - Copy fork folder, update meta.json
- `_load_reverie_globals()` - Parse dates, create maze, set step counter
- `_initialize_personas()` - Load personas from environment file
- `_setup_frontend_signaling()` - Write temp files for frontend

### #66 - Remove Debug Print Statements from Cognitive Modules

**Priority:** Medium
**Effort:** Low
**Dependencies:** None

**Affected Files:**
- `execute.py` - `print("aldhfoaf/????")`
- `retrieve.py` - Debug prints
- `reflect.py` - Multiple GNS FUNCTION prints
- `converse.py` - Date stamps and gibberish

**Actions:**
1. Remove all gibberish print statements
2. Convert useful debug output to `logging` module
3. Configure logging level via environment variable

### #67 - Clean Up Prompt Template Versions (v1/v2/v3)

**Priority:** Medium
**Effort:** Medium
**Dependencies:** None

**Problem:** Three versions exist with unclear status:
- `v1/` - Legacy, some still used
- `v2/` - Primary version
- `v3_ChatGPT/` - Partially implemented, mostly commented out

**Actions:**
1. Audit all templates and document usage
2. Either complete v3 migration OR standardize on v2
3. Remove unused templates
4. Clean up commented `########` blocks in `run_gpt_prompt.py`

### #68 - Split run_gpt_prompt.py into Smaller Modules

**Priority:** Low
**Effort:** High
**Dependencies:** #67

**Problem:** `run_gpt_prompt.py` is 3,328 lines (115 KB)

**Target Structure:**
```
prompt_template/
├── prompts/
│   ├── perceive.py
│   ├── plan.py
│   ├── reflect.py
│   ├── execute.py
│   └── converse.py
└── ...
```

### #69 - Add Missing production.py Django Settings File

**Priority:** Low
**Effort:** Low
**Dependencies:** #59

**Problem:** `settings/__init__.py` references `production.py` which doesn't exist

**Actions:**
1. Create `production.py` with secure defaults
2. OR simplify settings loading to remove production fallback

---

## Phase 4: Testing (Medium Priority)

These changes ensure reliability and enable confident refactoring.

### #73 - Set Up Test Infrastructure and CI

**Priority:** High (within phase)
**Effort:** Medium
**Dependencies:** None
**Blocking:** #70, #71, #72

**Actions:**
1. Create `tests/conftest.py` with shared fixtures
2. Organize test directory structure
3. Add dependencies: `uv add --group dev pytest-cov pytest-asyncio`
4. Create GitHub Actions workflow

### #70 - Add Tests for Cognitive Modules

**Priority:** Medium
**Effort:** High
**Dependencies:** #73

**Modules to Test:**
- `perceive.py` - Perception within vision radius
- `retrieve.py` - Memory retrieval and scoring
- `plan.py` - Schedule generation
- `reflect.py` - Importance threshold and insights
- `execute.py` - Action to movement conversion
- `converse.py` - Dialogue generation

### #71 - Add Tests for Memory Structures

**Priority:** Medium
**Effort:** Medium
**Dependencies:** #73

**Structures to Test:**
- `AssociativeMemory` - Event/thought/chat storage and retrieval
- `SpatialMemory` - World knowledge tree
- `Scratch` - Short-term state and hyperparameters

### #72 - Add Tests for Django Frontend Views

**Priority:** Low
**Effort:** Medium
**Dependencies:** #73

**Views to Test:**
- `landing()` - Landing page render
- `home()` - Simulator view
- `demo()` - Demo playback
- `process_environment()` - AJAX endpoint
- `update_environment()` - AJAX endpoint

---

## Implementation Order

```
Phase 1 (Critical - Do First)
│
├── #59 Fix Django security settings
├── #60 Add input validation
└── #61 Remove runtime.txt
│
Phase 2 (Foundational Structure)
│
├── #62 Rename environment/ to web/
│   │
│   └── #63 Move data directories
│       │
│       ├── #65 Add env var support for paths
│       │
│       └── #64 Remove duplicate global_methods.py
│
Phase 3 (Code Quality - Can parallelize)
│
├── #76 Extract CLI command handlers to commands module  ← NEW
├── #77 Extract path tester to utility module            ← NEW
├── #78 Refactor __init__ with helper methods            ← NEW
├── #66 Remove debug prints
├── #69 Add production.py
├── #67 Clean up prompt templates
│   │
│   └── #68 Split run_gpt_prompt.py
│
Phase 4 (Testing)
│
└── #73 Set up test infrastructure
    │
    ├── #70 Tests for cognitive modules
    ├── #71 Tests for memory structures
    └── #72 Tests for Django views
```

---

## Target Project Structure

After all phases are complete:

```
modern-stanford-agents-base/
├── src/
│   └── generative_agents/
│       ├── __init__.py
│       ├── config.py
│       ├── server.py
│       └── backend/
│           ├── commands/               # NEW: CLI command handlers (#76)
│           │   ├── __init__.py         # Command registry and dispatcher
│           │   ├── simulation.py       # run, save, fin, exit
│           │   ├── inspection.py       # print commands
│           │   └── tools.py            # call -- commands
│           ├── tools/                  # NEW: Development utilities (#77)
│           │   ├── __init__.py
│           │   └── path_tester.py      # Path tester utility
│           ├── persona/
│           │   ├── cognitive_modules/
│           │   ├── memory_structures/
│           │   └── prompt_template/
│           │       └── prompts/        # Split from run_gpt_prompt.py
│           ├── maze.py
│           ├── path_finder.py
│           └── utils.py
│
├── web/                                # Was: environment/frontend_server/
│   ├── manage.py
│   ├── config/                         # Was: frontend_server/frontend_server/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py           # NEW
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                            # Was: translator/
│   │   └── views.py
│   ├── templates/
│   └── static/
│
├── data/                               # NEW - Was inside frontend
│   ├── simulations/                    # Was: storage/
│   ├── compressed/                     # Was: compressed_storage/
│   └── temp/                           # Was: temp_storage/
│
├── assets/                             # NEW - Was: static_dirs/assets/
│   ├── maps/
│   └── characters/
│
├── tests/
│   ├── conftest.py                     # NEW
│   ├── unit/
│   │   ├── backend/
│   │   │   ├── cognitive/
│   │   │   └── memory/
│   │   └── frontend/
│   └── integration/
│
├── docs/
│   └── plan/
│       └── restructure-plan.md         # This file
│
├── .github/
│   └── workflows/
│       └── test.yml                    # NEW
│
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

---

## Risk Assessment

| Change | Risk Level | Mitigation |
|--------|------------|------------|
| Django security fixes | Low | Standard Django patterns |
| Directory restructure | Medium | Update all path references, test thoroughly |
| Removing duplicate code | Low | Verify all import sites |
| Splitting large files | Medium | Maintain backward-compatible re-exports |
| Adding tests | None | Additive change |

---

## Success Criteria

- [ ] All security vulnerabilities addressed (#59, #60)
- [ ] Clean project structure with clear separation of concerns
- [ ] No duplicate code files
- [ ] All paths configurable via environment variables
- [ ] No debug print statements in production code
- [ ] Test coverage > 50% for core modules
- [ ] CI pipeline running on all PRs
- [ ] Documentation updated to reflect new structure

---

## Notes

- No backward compatibility concerns - this is a new project
- All changes should be made incrementally with individual PRs
- Each PR should include documentation updates
- Run full test suite after each structural change
