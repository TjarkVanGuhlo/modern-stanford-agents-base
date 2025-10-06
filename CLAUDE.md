# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based simulation framework called "Generative Agents: Interactive Simulacra of Human Behavior" (also known as Reverie internally). It simulates believable human behaviors using LLM-powered agents that perceive, plan, reflect, and interact within a 2D game environment called Smallville.

Research paper: https://arxiv.org/abs/2304.03442

## Core Architecture

The codebase consists of two main servers that run concurrently:

### 1. Environment Server (Django)
- **Location**: `environment/frontend_server/`
- **Purpose**: Serves the visual map and handles frontend rendering
- **Tech**: Django 5.2.7+ project with SQLite database (modernized for Python 3.13)
- **Storage**:
  - `storage/` - saved simulations
  - `compressed_storage/` - compressed demos for replay
  - `static_dirs/assets/the_ville/` - world assets, maps, and agent history files

### 2. Simulation Server (Backend)
- **Location**: `reverie/backend_server/`
- **Entry point**: `reverie.py` - main simulation loop
- **Key classes**:
  - `ReverieServer` (reverie.py:42) - maintains all simulation state
  - `Persona` (persona/persona.py:30) - the generative agent class
  - `Maze` (maze.py:18) - 2D world representation

### Agent Cognitive Architecture

Agents (called "personas" internally) have a cognitive architecture with several modules:

**Memory Systems** (in `persona/memory_structures/`):
- `associative_memory.py` - Memory stream (event storage as temporal records)
- `spatial_memory.py` - Tree-based world knowledge
- `scratch.py` - Short-term/working memory

**Cognitive Modules** (in `persona/cognitive_modules/`):
- `perceive.py` - Perceive nearby events based on vision radius and attention bandwidth
- `retrieve.py` - Retrieve relevant memories
- `plan.py` - Generate plans and schedules
- `reflect.py` - Generate higher-level insights from memories
- `execute.py` - Execute actions in the world
- `converse.py` - Handle agent-to-agent conversations

**LLM Integration** (in `persona/prompt_template/`):
- `run_gpt_prompt.py` - High-level prompt execution functions
- `gpt_structure.py` - OpenAI API wrapper functions (using OpenAI SDK v2.x)

## Development Commands

### Setup
```bash
# Install dependencies (auto-creates .venv)
uv sync

# Verify installation
uv run python -c "import openai; print('Dependencies installed')"
```

### Running Tests
```bash
# Test OpenAI API connection
cd reverie/backend_server
uv run python test.py

# Django tests (if any)
cd environment/frontend_server
uv run python manage.py test
```

### Development Workflow
```bash
# Add new dependency
uv add <package-name>

# Update all dependencies
uv sync --upgrade

# Run any Python script
uv run python <script.py>
```

## Initial Configuration

1. **Create `.env` file in project root**:
```bash
OPENAI_API_KEY=your_openai_api_key_here
KEY_OWNER=Your Name
```

The `utils.py` file loads these secrets automatically via `python-dotenv`.

Required Python: >=3.13

### Configurable Cognitive Models

The system supports configuring different LLM models for each cognitive function. Add to `.env`:

```bash
MODEL_PERCEIVE=gpt-4o-mini          # Fast perception for frequent operations
MODEL_RETRIEVE_EMBEDDING=text-embedding-3-large  # High-quality memory retrieval
MODEL_PLAN=gpt-4o                   # Complex planning tasks
MODEL_REFLECT=gpt-4o                # Deep reflection and insights
MODEL_EXECUTE=gpt-4o-mini           # Fast execution for frequent operations
MODEL_CONVERSE=gpt-4o               # Natural conversations between agents
```

These models are loaded in `reverie/backend_server/utils.py` and used throughout the cognitive modules.

## Running the Simulation

### Start Environment Server
```bash
cd environment/frontend_server
uv run python manage.py runserver
```
Verify at http://localhost:8000/ - should show "Your environment server is up and running"

### Start Simulation Server
```bash
cd reverie/backend_server
uv run python reverie.py
```

When prompted for simulation names:
- **Fork simulation**: `base_the_ville_isabella_maria_klaus` (3 agents) or `base_the_ville_n25` (25 agents)
- **New simulation name**: Choose any name (e.g., `test-simulation`)

### Simulation Commands
Navigate to http://localhost:8000/simulator_home

**Interactive Commands** (at the `Enter option:` prompt):
- `run <step-count>` - Run simulation for N steps (1 step = 10 seconds game time)
- `fin` - Save simulation and exit
- `exit` - Exit without saving
- `call -- load history the_ville/<file>.csv` - Load agent memories from CSV

Example files for loading history:
- `agent_history_init_n3.csv` (3-agent simulation)
- `agent_history_init_n25.csv` (25-agent simulation)
Located in: `environment/frontend_server/static_dirs/assets/the_ville/`

## Replay & Demo

### Replay (for debugging, sprites not optimized)
```
http://localhost:8000/replay/<simulation-name>/<starting-time-step>/
```

### Demo (proper character sprites, must compress first)
```bash
# Compress simulation
cd reverie
uv run python compress_sim_storage.py
# Edit the compress() function call with your simulation name

# View demo
http://localhost:8000/demo/<simulation-name>/<starting-time-step>/<speed>
```
Speed: 1 (slowest) to 5 (fastest)

## Key Concepts

**Simulation Flow**:
1. Fork from a base simulation (or previous simulation)
2. Each step: agents perceive → retrieve memories → plan → execute → reflect
3. All agent state stored in `storage/<simulation-name>/` with JSON/CSV files

**World Structure**:
- 2D tile-based maze defined in `environment/frontend_server/static_dirs/assets/the_ville/matrix/`
- World has hierarchical structure: World → Sector → Arena → Game Object
- Maps created with Tiled map editor
- Special blocks defined in CSV files map tile colors to semantic locations

**Agent Memory**:
- Events stored with format: `[event.type, event.created, event.expiration, subject, predicate, object]`
- Memories have poignancy scores (importance) that affect retrieval
- Retention period prevents re-perceiving same events

## Modernization Notes

This codebase has been modernized from the original Stanford research code:
- **Python**: Upgraded from 3.9 to 3.13+
- **Dependency Management**: Migrated from `requirements.txt` to `uv` and `pyproject.toml`
- **Secrets Management**: Environment variables via `.env` file (using `python-dotenv`)
- **OpenAI SDK**: Upgraded from v0.27.0 to v2.x with modern client pattern
- **Django**: Updated from 2.2 to 5.2.7 (removed deprecated imports)
- **Model Configuration**: LLMs configurable per cognitive function via environment variables

## Debugging & Troubleshooting

### Common Issues

**OpenAI API Errors**:
- Check `.env` file exists and contains valid `OPENAI_API_KEY`
- Verify API key permissions and rate limits
- Test connection: `cd reverie/backend_server && uv run python test.py`

**Django Server Issues**:
- Database migrations: `cd environment/frontend_server && uv run python manage.py migrate`
- Static files issues: Check `static_dirs/` permissions
- Port conflicts: Ensure port 8000 is available

**Simulation Freezes**:
- API rate limits - save frequently with `fin` command
- Memory issues with 25-agent simulations - use 3-agent base for testing

### File Locations

**Key Files**:
- Agent state: `storage/<simulation-name>/personas/<agent-name>/`
- World map data: `environment/frontend_server/static_dirs/assets/the_ville/matrix/`
- Agent memories: JSON files in `storage/<simulation-name>/personas/*/memory/`
- Simulation checkpoints: `storage/<simulation-name>/reverie/meta.json`

## Cost & API Considerations

- OpenAI API calls can be rate-limited - save simulations frequently
- Running simulations can be costly, especially with many agents
- Current implementation uses OpenAI chat.completions API with configurable models (default: gpt-4o and gpt-4o-mini)
- Estimate: ~$0.50-$2.00 per hour for 3-agent simulation, ~$5-10 per hour for 25 agents

## GitHub Configuration

This repo uses the TjarkVanGuhlo GitHub account. See TJARK_SETUP.md for GitHub CLI authentication and 1Password SSH setup details.
