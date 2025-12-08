# Project Restructure Plan

This document outlines the comprehensive plan to restructure the modern-stanford-agents-base project following Python best practices. The plan is organized into phases with clear dependencies and priorities.

## Executive Summary

The project requires structural improvements in five key areas:
1. **Security** - Critical Django vulnerabilities need immediate attention
2. **Structure** - Directory layout needs clarification and simplification
3. **Code Quality** - Technical debt and maintenance issues
4. **Testing** - Comprehensive test coverage is missing
5. **User Experience** - CLI and developer tooling improvements

## Current Issues Overview

| Phase | Issues | Priority |
|-------|--------|----------|
| Security | #61 | Critical |
| Structure | #62, #63, #64, #65 | High |
| Code Quality | #66, #67, #68, #69, #77, #78 | Medium |
| Testing | #70, #71, #72, #73 | Medium |
| User Experience | #80, #81 | Medium |

---

## Phase 1: Security (Critical)

These issues must be resolved before any deployment or public access.

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

## Phase 5: User Experience (Medium Priority)

These changes improve the developer and researcher experience.

### #80 - Improve CLI Startup UX with Interactive Simulation Selection

**Priority:** High (within phase)
**Effort:** Medium
**Dependencies:** None

**Problem:** Current CLI requires manually typing exact simulation names, which is error-prone and cumbersome.

**Current State:**
```python
def main():
    origin = input("Enter the name of the forked simulation: ").strip()
    target = input("Enter the name of the new simulation: ").strip()
```

**Solution:** Use **questionary** (v2.1.1, actively maintained) for interactive selection:
- Arrow key navigation through available simulations
- Base simulations (`base_*`) shown separately from saved simulations
- Metadata display (persona count, step count)
- Type-ahead filtering
- Auto-generated names with timestamps
- CLI arguments for automation (`--fork`, `--name`, `--list`)

**Library Choice:**
| Library | Status | Decision |
|---------|--------|----------|
| questionary | v2.1.1 (Aug 2025) | **Selected** - lightweight, maintained |
| Textual | v6.3.0 (Dec 2025) | Overkill for selection menu |
| InquirerPy | 12+ months stale | Avoid |
| simple-term-menu | 12+ months stale | Avoid |

### #81 - Build Textual-based Simulation Dashboard

**Priority:** Low
**Effort:** High
**Dependencies:** #80

**Vision:** A rich terminal UI for real-time simulation monitoring:
- Agent activity monitoring (current actions, locations, conversations)
- Memory inspection (associative, spatial, scratch)
- Interactive controls (pause, step, save, speed adjustment)
- Log streaming with filtering

**Library:** Textual (v6.3.0, Dec 2025, 32.7k GitHub stars, very actively maintained)

**Features:**
- Real-time simulation status display
- Agent list with status indicators
- Agent detail panel (location, action, plan, memories)
- Keyboard shortcuts for common actions
- Can deploy to web browser via textual-web

---

## Implementation Order

```
Phase 1 (Critical - Do First)
│
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
├── #77 Extract path tester to utility module
├── #78 Refactor __init__ with helper methods
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
│
Phase 5 (User Experience)
│
├── #80 Interactive simulation selection (questionary)
│   │
│   └── #81 Textual simulation dashboard
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
│           ├── commands/               # CLI command handlers
│           │   ├── __init__.py         # Command registry and dispatcher
│           │   ├── simulation.py       # run, save, fin, exit
│           │   ├── inspection.py       # print commands
│           │   └── tools.py            # call -- commands
│           ├── tools/                  # Development utilities (#77)
│           │   ├── __init__.py
│           │   └── path_tester.py      # Path tester utility
│           ├── persona/
│           │   ├── cognitive_modules/
│           │   ├── memory_structures/
│           │   └── prompt_template/
│           │       └── prompts/        # Split from run_gpt_prompt.py (#68)
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
│   │   │   └── production.py           # #69
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
│   ├── conftest.py                     # #73
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
│       └── test.yml                    # #73
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

- [x] All security vulnerabilities addressed
- [ ] Clean project structure with clear separation of concerns (#62, #63)
- [ ] No duplicate code files (#64)
- [ ] All paths configurable via environment variables (#65)
- [ ] No debug print statements in production code (#66)
- [ ] Test coverage > 50% for core modules (#70, #71, #72)
- [ ] CI pipeline running on all PRs (#73)
- [ ] Documentation updated to reflect new structure

---

## Notes

- No backward compatibility concerns - this is a new project
- All changes should be made incrementally with individual PRs
- Each PR should include documentation updates
- Run full test suite after each structural change
