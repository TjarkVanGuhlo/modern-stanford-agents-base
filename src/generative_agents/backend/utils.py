import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _find_project_root() -> Path:
    """Find the project root directory (contains pyproject.toml)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not find project root (no pyproject.toml found)")


PROJECT_ROOT = _find_project_root()
ENVIRONMENT_DIR = PROJECT_ROOT / "environment" / "frontend_server"

# OpenAI API Configuration (loaded from .env - these are actual secrets)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY environment variable is required. Please set it in your .env file."
    )

key_owner = os.getenv("KEY_OWNER")
if not key_owner:
    raise ValueError(
        "KEY_OWNER environment variable is required. Please set it in your .env file."
    )

# Path Configuration (using pathlib for proper path handling)
maze_assets_loc = ENVIRONMENT_DIR / "static_dirs" / "assets"
env_matrix = maze_assets_loc / "the_ville" / "matrix"
env_visuals = maze_assets_loc / "the_ville" / "visuals"

fs_storage = ENVIRONMENT_DIR / "storage"
fs_temp_storage = ENVIRONMENT_DIR / "temp_storage"

collision_block_id = "32125"

# Import cognitive models from config (these are configuration, not secrets)

# Verbose
debug = True
