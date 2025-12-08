"""Base types for the command system."""

from dataclasses import dataclass
from enum import Enum, auto


class CommandAction(Enum):
    """Post-command actions for the REPL loop."""

    CONTINUE = auto()
    EXIT_SAVE = auto()
    EXIT_NO_SAVE = auto()
    PATH_TESTER = auto()


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Result of command execution."""

    output: str = ""
    action: CommandAction = CommandAction.CONTINUE

    @classmethod
    def ok(cls, output: str = "") -> "CommandResult":
        """Create a result that continues the REPL loop."""
        return cls(output=output)

    @classmethod
    def exit_save(cls, output: str = "") -> "CommandResult":
        """Create a result that exits after saving."""
        return cls(output=output, action=CommandAction.EXIT_SAVE)

    @classmethod
    def exit_no_save(cls, output: str = "") -> "CommandResult":
        """Create a result that exits without saving."""
        return cls(output=output, action=CommandAction.EXIT_NO_SAVE)

    @classmethod
    def path_tester(cls) -> "CommandResult":
        """Create a result that enters path tester mode."""
        return cls(action=CommandAction.PATH_TESTER)
