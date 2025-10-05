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
- **Tech**: Django 2.2 project with SQLite database
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
- `run_gpt_prompt.py` - OpenAI API calls
- `gpt_structure.py` - Prompt templates

## Development Setup

### Initial Configuration

1. **Create `.env` file in project root**:
```bash
OPENAI_API_KEY=your-api-key-here
KEY_OWNER=Your Name
```

2. **Optional: Configure cognitive models** (add to `.env`):
```bash
# Default models (used if not specified)
MODEL_PERCEIVE=gpt-4o-mini
MODEL_RETRIEVE_EMBEDDING=text-embedding-3-large
MODEL_PLAN=gpt-4o
MODEL_REFLECT=gpt-4o
MODEL_EXECUTE=gpt-4o-mini
MODEL_CONVERSE=gpt-4o

# Example: Use smaller embedding for cost savings
MODEL_RETRIEVE_EMBEDDING=text-embedding-3-small
```

3. **Install dependencies**:
```bash
uv sync
```
Requires Python 3.13+. Uses `uv` for dependency management.

## Running the Simulation

### Start Environment Server
```bash
cd environment/frontend_server
python manage.py runserver
```
Verify at http://localhost:8000/ - should show "Your environment server is up and running"

### Start Simulation Server
```bash
cd reverie/backend_server
python reverie.py
```

When prompted for simulation names:
- **Fork simulation**: `base_the_ville_isabella_maria_klaus` (3 agents) or `base_the_ville_n25` (25 agents)
- **New simulation name**: Choose any name (e.g., `test-simulation`)

### Run Simulation Steps
Navigate to http://localhost:8000/simulator_home

At the `Enter option:` prompt, run:
```bash
run <step-count>
```
One game step = 10 seconds of game time.

Save and exit: `fin`
Exit without saving: `exit`

### Load Agent History (Optional)
To initialize agents with custom memories:
```bash
call -- load history the_ville/<history_file_name>.csv
```
Example files: `agent_history_init_n3.csv` or `agent_history_init_n25.csv` in `environment/frontend_server/static_dirs/assets/the_ville/`

## Replay & Demo

### Replay (for debugging, sprites not optimized)
```
http://localhost:8000/replay/<simulation-name>/<starting-time-step>/
```

### Demo (proper character sprites, must compress first)
1. Compress simulation using `reverie/compress_sim_storage.py`
2. Navigate to:
```
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

## Cost & API Considerations

- OpenAI API can hang when hitting rate limits - save simulations frequently
- Running simulations can be costly, especially with many agents (as of early 2023)

## GitHub Configuration

This repo uses the TjarkVanGuhlo GitHub account. See TJARK_SETUP.md for GitHub CLI authentication details.
