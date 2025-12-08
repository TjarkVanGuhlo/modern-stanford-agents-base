"""Inspection commands for viewing persona and world state."""

from typing import TYPE_CHECKING

from . import registry
from .base import CommandResult

if TYPE_CHECKING:
    from generative_agents.backend.server import ReverieServer


# --- Persona Schedule Commands ---


@registry.register(
    "print persona schedule",
    match_prefix=True,
    help_text="Show decomposed schedule (e.g., 'print persona schedule Isabella Rodriguez')",
)
def cmd_print_persona_schedule(server: "ReverieServer", command: str) -> CommandResult:
    """Print the decomposed daily schedule of a persona."""
    persona_name = " ".join(command.split()[-2:])
    output = server.personas[persona_name].scratch.get_str_daily_schedule_summary()
    return CommandResult.ok(output)


@registry.register(
    "print all persona schedule",
    help_text="Show decomposed schedules for all personas",
)
def cmd_print_all_persona_schedule(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print schedules for all personas."""
    lines = []
    for persona_name, persona in server.personas.items():
        lines.extend(
            (
                persona_name,
                persona.scratch.get_str_daily_schedule_summary(),
                "---",
            )
        )
    return CommandResult.ok("\n".join(lines))


@registry.register(
    "print hourly org persona schedule",
    match_prefix=True,
    help_text="Show hourly schedule (e.g., 'print hourly org persona schedule Isabella Rodriguez')",
)
def cmd_print_hourly_org_persona_schedule(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the hourly (non-decomposed) schedule of a persona."""
    persona_name = " ".join(command.split()[-2:])
    output = server.personas[
        persona_name
    ].scratch.get_str_daily_schedule_hourly_org_summary()
    return CommandResult.ok(output)


# --- Persona State Commands ---


@registry.register(
    "print persona current tile",
    match_prefix=True,
    help_text="Show persona position (e.g., 'print persona current tile Isabella Rodriguez')",
)
def cmd_print_persona_current_tile(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the current tile of a persona."""
    persona_name = " ".join(command.split()[-2:])
    output = str(server.personas[persona_name].scratch.curr_tile)
    return CommandResult.ok(output)


@registry.register(
    "print persona chatting with buffer",
    match_prefix=True,
    help_text="Show chat buffer (e.g., 'print persona chatting with buffer Isabella Rodriguez')",
)
def cmd_print_persona_chatting_with_buffer(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the chatting with buffer of a persona."""
    persona_name = " ".join(command.split()[-2:])
    curr_persona = server.personas[persona_name]
    lines = [
        f"{p_n}: {count}"
        for p_n, count in curr_persona.scratch.chatting_with_buffer.items()
    ]
    return CommandResult.ok("\n".join(lines))


# --- Associative Memory Commands ---


@registry.register(
    "print persona associative memory (event)",
    match_prefix=True,
    help_text="Show event memories (e.g., 'print persona associative memory (event) Isabella Rodriguez')",
)
def cmd_print_persona_associative_memory_event(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the associative memory events of a persona."""
    persona_name = " ".join(command.split()[-2:])
    persona = server.personas[persona_name]
    output = f"{persona}\n{persona.a_mem.get_str_seq_events()}"
    return CommandResult.ok(output)


@registry.register(
    "print persona associative memory (thought)",
    match_prefix=True,
    help_text="Show thought memories (e.g., 'print persona associative memory (thought) Isabella Rodriguez')",
)
def cmd_print_persona_associative_memory_thought(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the associative memory thoughts of a persona."""
    persona_name = " ".join(command.split()[-2:])
    persona = server.personas[persona_name]
    output = f"{persona}\n{persona.a_mem.get_str_seq_thoughts()}"
    return CommandResult.ok(output)


@registry.register(
    "print persona associative memory (chat)",
    match_prefix=True,
    help_text="Show chat memories (e.g., 'print persona associative memory (chat) Isabella Rodriguez')",
)
def cmd_print_persona_associative_memory_chat(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the associative memory chats of a persona."""
    persona_name = " ".join(command.split()[-2:])
    persona = server.personas[persona_name]
    output = f"{persona}\n{persona.a_mem.get_str_seq_chats()}"
    return CommandResult.ok(output)


@registry.register(
    "print persona spatial memory",
    match_prefix=True,
    help_text="Show spatial memory tree (e.g., 'print persona spatial memory Isabella Rodriguez')",
)
def cmd_print_persona_spatial_memory(
    server: "ReverieServer", command: str
) -> CommandResult:
    """Print the spatial memory of a persona."""
    persona_name = " ".join(command.split()[-2:])
    # Note: print_tree() prints directly, doesn't return string
    server.personas[persona_name].s_mem.print_tree()
    return CommandResult.ok()


# --- World State Commands ---


@registry.register(
    "print current time",
    help_text="Show simulation time and step count",
)
def cmd_print_current_time(server: "ReverieServer", command: str) -> CommandResult:
    """Print the current simulation time."""
    output = f"{server.curr_time.strftime('%B %d, %Y, %H:%M:%S')}\nsteps: {server.step}"
    return CommandResult.ok(output)


@registry.register(
    "print tile event",
    match_prefix=True,
    help_text="Show tile events (e.g., 'print tile event 50, 30')",
)
def cmd_print_tile_event(server: "ReverieServer", command: str) -> CommandResult:
    """Print events at a tile coordinate."""
    # Extract coordinates after "print tile event"
    coords_str = command[len("print tile event") :].strip()
    coords = [int(i.strip()) for i in coords_str.split(",")]
    coordinate = (coords[0], coords[1])
    lines = [str(event) for event in server.maze.access_tile(coordinate)["events"]]
    return CommandResult.ok("\n".join(lines))


@registry.register(
    "print tile details",
    match_prefix=True,
    help_text="Show tile details (e.g., 'print tile details 50, 30')",
)
def cmd_print_tile_details(server: "ReverieServer", command: str) -> CommandResult:
    """Print all details of a tile."""
    # Extract coordinates after "print tile details"
    coords_str = command[len("print tile details") :].strip()
    coords = [int(i.strip()) for i in coords_str.split(",")]
    coordinate = (coords[0], coords[1])
    lines = [
        f"{key}: {val}" for key, val in server.maze.access_tile(coordinate).items()
    ]
    return CommandResult.ok("\n".join(lines))
