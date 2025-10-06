import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration (loaded from .env - these are actual secrets)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")

key_owner = os.getenv("KEY_OWNER")
if not key_owner:
    raise ValueError("KEY_OWNER environment variable is required. Please set it in your .env file.")

# Path Configuration
maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Import cognitive models from config (these are configuration, not secrets)
from config import (
    MODEL_PERCEIVE,
    MODEL_RETRIEVE_EMBEDDING,
    MODEL_PLAN,
    MODEL_REFLECT,
    MODEL_EXECUTE,
    MODEL_CONVERSE,
    model_config
)

# Verbose
debug = True
