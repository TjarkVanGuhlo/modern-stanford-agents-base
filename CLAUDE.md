# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modernized Python 3.13+ implementation of "Generative Agents: Interactive Simulacra of Human Behavior" (Park et al., 2023). The system simulates believable human behaviors using LLM-powered agents that perceive, remember, plan, reflect, and interact in a 2D virtual world called Smallville.

## Common Commands

### Development Setup
```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run commands inside the virtual environment
uv run <command>

# Add dependencies
uv add <package>              # Runtime dependency
uv add --group dev <package>  # Dev dependency
```

### Running Tests
```bash
# Run full test suite
uv run pytest -q

# Run specific test file
uv run pytest tests/test_integration.py -q

# Run tests by keyword
uv run pytest -k "model_config" -q

# Show stdout on failure
uv run pytest -rP
```

### Running the Simulation

**Start Frontend Environment Server (Django):**
```bash
cd environment/frontend_server
uv run python manage.py runserver
```
Visit http://localhost:8000/ to verify it's running.

**Start Backend Simulation Server:**
```bash
cd reverie/backend_server
uv run python reverie.py
```
Follow the prompts to load a base simulation (e.g., `base_the_ville_isabella_maria_klaus`) and name your new simulation.

**Run Simulation Steps:**
In the backend server prompt, enter:
```
run <step-count>
```
One step = 10 seconds of game time. View agents at http://localhost:8000/simulator_home

**Save and Exit:**
```
fin     # Save and exit
save    # Save without exiting
exit    # Exit without saving (deletes current simulation)
```

## Architecture

### Core Cognitive Loop

The system implements a perceive-retrieve-plan-reflect-execute cycle for each agent at every time step:

1. **Perceive** (`persona/cognitive_modules/perceive.py`): Agent observes nearby events within vision radius, filtered by attention bandwidth and retention
2. **Retrieve** (`persona/cognitive_modules/retrieve.py`): Queries associative memory using embeddings to find relevant past events and thoughts
3. **Plan** (`persona/cognitive_modules/plan.py`): Generates long-term (daily schedule) and short-term (immediate action) plans based on retrieved context
4. **Reflect** (`persona/cognitive_modules/reflect.py`): Synthesizes memories into higher-level thoughts when importance threshold is reached
5. **Execute** (`persona/cognitive_modules/execute.py`): Converts plans into concrete actions (object usage, tile movement)
6. **Converse** (`persona/cognitive_modules/converse.py`): Handles agent-to-agent dialogue and social interaction

### Key Components

**Persona** (`reverie/backend_server/persona/persona.py`):
- The main agent class (internally called "Persona", publicly "GenerativeAgent")
- Integrates three memory types: spatial (world layout), associative (event stream), and scratch (short-term working memory)
- Each agent has configurable `att_bandwidth` (attention capacity) and `retention` (memory recency threshold)

**Memory Structures**:
- **AssociativeMemory** (`persona/memory_structures/associative_memory.py`): The "memory stream" from the paper. Stores ConceptNodes with embeddings, keywords, poignancy scores, and decay functions. Three types: events, thoughts, chats
- **SpatialMemory** (`persona/memory_structures/spatial_memory.py`): Hierarchical tree of world→sector→arena→game objects
- **Scratch** (`persona/memory_structures/scratch.py`): Transient state including current action, planned path, daily schedule

**Maze** (`reverie/backend_server/maze.py`):
- 2D tile-based world representation loaded from Tiled map exports
- Each tile contains: world/sector/arena/game_object addresses, collision state, active events
- Handles pathfinding via `path_finder.py` using collision detection

**ReverieServer** (`reverie/backend_server/reverie.py`):
- Main simulation orchestrator
- Synchronizes frontend (Django) and backend (agent logic)
- Manages time progression (default: 10 seconds per step)
- Coordinates multi-agent interactions and environment state

### Model Configuration

Models are configured in `reverie/backend_server/config.py` via the `ModelConfig` class, **not** in .env (they are configuration choices, not secrets).

**Cognitive Functions and Models**:
| Function | Default Model | Purpose |
|----------|---------------|---------|
| PERCEIVE | gpt-4o-mini | Environment observation |
| RETRIEVE_EMBEDDING | text-embedding-3-large | Memory retrieval similarity |
| PLAN | gpt-4o | Action planning |
| REFLECT | gpt-4o | Memory synthesis |
| EXECUTE | gpt-4o-mini | Action execution |
| CONVERSE | gpt-4o | Dialogue |

**Environment-Based Configuration**:
```bash
# Use presets: performance, balanced (default), economy
MODEL_PRESET=economy

# Override individual models
MODEL_REFLECT=gpt-4o-mini
MODEL_RETRIEVE_EMBEDDING=text-embedding-3-small
```

Configuration is read at import time. In tests, ensure clean imports by clearing `sys.modules` when testing different configurations.

### Data Flow

1. Frontend server (`environment/frontend_server`) serves the Django UI and stores simulation state in `storage/` and `compressed_storage/`
2. Backend server reads environment JSON files (`environment/<step>.json`) to get agent positions
3. Each agent executes cognitive cycle, returning movement decisions
4. Backend writes movement JSON files (`movement/<step>.json`) for frontend
5. Time advances by `sec_per_step` (default: 10 seconds)

## Testing Conventions

- Tests use `pytest` from the `dev` dependency group
- Many tests prepend `sys.path` to import backend modules directly:
  ```python
  sys.path.insert(0, 'reverie/backend_server')
  ```
- Mock all OpenAI calls by patching `gpt_structure.client`
- When testing config changes, clear affected modules from `sys.modules` before re-importing (`['config', 'utils', 'gpt_structure']`)
- Set `OPENAI_API_KEY` and `KEY_OWNER` via `patch.dict(os.environ)` to avoid host environment dependencies

## Important Patterns

**Path Addresses**: Locations are specified as colon-separated hierarchical paths:
```
world:sector:arena:game_object
# Example: "double studio:double studio:bedroom 2:bed"
```

**Event Triples**: Events are stored as `(subject, predicate, object, description)` tuples:
```python
('Isabella Rodriguez', 'is', 'sleeping', 'sleeping in her bed')
```

**Forking Simulations**: All simulations fork from a base simulation (hand-crafted initial state). New simulations copy the fork and modify `meta.json`.

**Agent History Loading**: Use `call -- load history the_ville/<file>.csv` in the server prompt to batch-load semicolon-separated memory records for agents.

## Environment Variables

Required in `.env` at project root:
```bash
OPENAI_API_KEY=your-api-key-here
KEY_OWNER=Your Name
```

Optional model configuration (see Model Configuration section above):
```bash
MODEL_PRESET=balanced|performance|economy
MODEL_PERCEIVE=gpt-4o-mini
# ... etc for other cognitive functions
```

## Storage Locations

- Simulations: `environment/frontend_server/storage/`
- Compressed demos: `environment/frontend_server/compressed_storage/`
- Maze assets: `environment/frontend_server/static_dirs/assets/`
- Temp storage: `environment/frontend_server/temp_storage/`

## Debugging Commands

The backend server (`reverie.py`) provides an interactive REPL with commands:

```
print persona schedule <name>              # Show decomposed daily schedule
print all persona schedule                 # Show all agent schedules
print persona associative memory (event) <name>
print persona associative memory (thought) <name>
print persona associative memory (chat) <name>
print persona spatial memory <name>        # Show world knowledge tree
print current time                         # Show simulation time and step count
print tile event <x>, <y>                  # Show events at tile coordinate
call -- analysis <name>                    # Start stateless chat with agent
call -- load history the_ville/<file>.csv  # Batch load agent memories
```

## Key Technical Details

- Python requires >= 3.13 (uses modern features like pattern matching where appropriate)
- All LLM calls centralized in `gpt_structure.py` for easy mocking
- Simulations are deterministic given the same seed and OpenAI API responses
- Agents can perceive within a vision radius (default: 8 tiles)
- Memory retrieval uses embedding similarity + recency + importance weighting
- Reflection is triggered when cumulative importance exceeds threshold (default: 150)
- Path planning uses A* algorithm with collision avoidance

## Version and Release Policy

See `.junie/guidelines.md` for:
- Tag naming conventions (must be `v<major>.<minor>.<patch>`)
- Release numbering policy (no test releases; production only)
- GitHub CLI setup for TjarkVanGuhlo account
