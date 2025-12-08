"""Development and utility commands."""

import shutil
from typing import TYPE_CHECKING

from generative_agents.backend.global_methods import read_file_to_list
from generative_agents.backend.persona.cognitive_modules.converse import (
    load_history_via_whisper,
)
from generative_agents.backend.utils import maze_assets_loc

from . import registry
from .base import CommandResult

if TYPE_CHECKING:
    from generative_agents.backend.server import ReverieServer


@registry.register(
    "start path tester mode",
    help_text="Enter path testing mode (for map development)",
)
def cmd_start_path_tester_mode(server: "ReverieServer", command: str) -> CommandResult:
    """Start the path tester mode."""
    shutil.rmtree(server.sim_folder)
    return CommandResult.path_tester()


@registry.register(
    "call -- analysis",
    match_prefix=True,
    help_text="Start stateless chat with persona (e.g., 'call -- analysis Isabella Rodriguez')",
)
def cmd_call_analysis(server: "ReverieServer", command: str) -> CommandResult:
    """Start an analysis chat session with a persona."""
    persona_name = command[len("call -- analysis") :].strip()
    server.personas[persona_name].open_convo_session("analysis")
    return CommandResult.ok()


@registry.register(
    "call -- load history",
    match_prefix=True,
    help_text="Load history from CSV (e.g., 'call -- load history the_ville/agent_history_init_n3.csv')",
)
def cmd_call_load_history(server: "ReverieServer", command: str) -> CommandResult:
    """Load agent history from a CSV file."""
    file_path = command[len("call -- load history") :].strip()
    curr_file = f"{maze_assets_loc}/{file_path}"

    rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
    clean_whispers = []
    for row in rows:
        agent_name = row[0].strip()
        whispers = row[1].split(";")
        whispers = [whisper.strip() for whisper in whispers]
        clean_whispers.extend([agent_name, whisper] for whisper in whispers)
    load_history_via_whisper(server.personas, clean_whispers)
    return CommandResult.ok(f"Loaded history from {file_path}")


@registry.register(
    "help",
    aliases=["?", "h"],
    help_text="Show available commands",
)
def cmd_help(server: "ReverieServer", command: str) -> CommandResult:
    """Show help for all commands."""
    from . import get_help

    return CommandResult.ok(get_help())
