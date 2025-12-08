"""Simulation control commands: run, save, fin, exit."""

import shutil
from typing import TYPE_CHECKING

from . import registry
from .base import CommandResult

if TYPE_CHECKING:
    from generative_agents.backend.server import ReverieServer


@registry.register(
    "fin",
    aliases=["f", "finish", "save and finish"],
    help_text="Save simulation and exit",
)
def cmd_fin(server: "ReverieServer", command: str) -> CommandResult:
    """Save and exit the simulation."""
    server.save()
    return CommandResult.exit_save()


@registry.register("exit", help_text="Exit without saving (deletes simulation)")
def cmd_exit(server: "ReverieServer", command: str) -> CommandResult:
    """Exit without saving and delete simulation folder."""
    shutil.rmtree(server.sim_folder)
    return CommandResult.exit_no_save()


@registry.register("save", help_text="Save current simulation progress")
def cmd_save(server: "ReverieServer", command: str) -> CommandResult:
    """Save simulation progress."""
    server.save()
    return CommandResult.ok("Saved.")


@registry.register(
    "run", match_prefix=True, help_text="Run N simulation steps (e.g., 'run 100')"
)
def cmd_run(server: "ReverieServer", command: str) -> CommandResult:
    """Run simulation for specified number of steps."""
    int_count = int(command.split()[-1])
    server.start_server(int_count)
    return CommandResult.ok()
