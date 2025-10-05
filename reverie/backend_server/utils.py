import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration (loaded from .env)
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

# Generative Agent Cognitive Models
# Configure models for different cognitive functions (perceive, retrieve, plan, reflect, execute, converse)
MODEL_PERCEIVE = os.getenv("MODEL_PERCEIVE", "gpt-4o-mini")
MODEL_RETRIEVE_EMBEDDING = os.getenv("MODEL_RETRIEVE_EMBEDDING", "text-embedding-3-large")
MODEL_PLAN = os.getenv("MODEL_PLAN", "gpt-4o")
MODEL_REFLECT = os.getenv("MODEL_REFLECT", "gpt-4o")
MODEL_EXECUTE = os.getenv("MODEL_EXECUTE", "gpt-4o-mini")
MODEL_CONVERSE = os.getenv("MODEL_CONVERSE", "gpt-4o")

# Verbose
debug = True
