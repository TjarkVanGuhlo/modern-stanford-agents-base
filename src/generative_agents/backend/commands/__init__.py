"""Command registry and dispatcher for the simulation CLI."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import CommandAction, CommandResult

if TYPE_CHECKING:
    from generative_agents.backend.server import ReverieServer

# Type alias for command handlers
CommandHandler = Callable[["ReverieServer", str], CommandResult]


@dataclass
class Command:
    """A registered command."""

    name: str
    handler: CommandHandler
    help_text: str = ""
    aliases: list[str] = field(default_factory=list)
    match_prefix: bool = False


class CommandRegistry:
    """Registry for CLI commands."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._prefix_commands: list[Command] = []

    def register(
        self,
        name: str,
        *,
        aliases: list[str] | None = None,
        help_text: str = "",
        match_prefix: bool = False,
    ) -> Callable[[CommandHandler], CommandHandler]:
        """Decorator to register a command handler."""

        def decorator(func: CommandHandler) -> CommandHandler:
            cmd = Command(
                name=name,
                handler=func,
                help_text=help_text,
                aliases=aliases or [],
                match_prefix=match_prefix,
            )
            self._commands[name.lower()] = cmd
            for alias in cmd.aliases:
                self._commands[alias.lower()] = cmd
            if match_prefix:
                self._prefix_commands.append(cmd)
            return func

        return decorator

    def dispatch(self, server: "ReverieServer", command: str) -> CommandResult | None:
        """Dispatch a command to its handler. Returns None if no match."""
        cmd_lower = command.lower().strip()

        # Try exact match first
        for name, cmd in self._commands.items():
            if not cmd.match_prefix and cmd_lower == name:
                return cmd.handler(server, command)

        # Try prefix match (sorted by name length descending for longest match)
        for cmd in sorted(
            self._prefix_commands, key=lambda c: len(c.name), reverse=True
        ):
            if cmd_lower.startswith(cmd.name.lower()):
                return cmd.handler(server, command)
            for alias in cmd.aliases:
                if cmd_lower.startswith(alias.lower()):
                    return cmd.handler(server, command)

        return None

    def get_help(self) -> str:
        """Generate help text for all commands."""
        seen: set[str] = set()
        lines = ["Available commands:", ""]
        for cmd in self._commands.values():
            if cmd.name in seen:
                continue
            seen.add(cmd.name)
            alias_str = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            lines.append(f"  {cmd.name}{alias_str}")
            if cmd.help_text:
                lines.append(f"    {cmd.help_text}")
        return "\n".join(lines)


# Global registry
registry = CommandRegistry()

# Import command modules to register them (must be after registry creation)
from . import inspection  # noqa: E402, F401
from . import simulation  # noqa: E402, F401
from . import tools  # noqa: E402, F401


def dispatch(server: "ReverieServer", command: str) -> CommandResult | None:
    """Dispatch a command to its handler."""
    return registry.dispatch(server, command)


def get_help() -> str:
    """Get help text for all commands."""
    return registry.get_help()


__all__ = [
    "CommandAction",
    "CommandResult",
    "dispatch",
    "get_help",
    "registry",
]
