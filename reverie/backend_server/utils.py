import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration (loaded from .env)
openai_api_key = os.getenv("OPENAI_API_KEY")
key_owner = os.getenv("KEY_OWNER")

# Path Configuration
maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose
debug = True
