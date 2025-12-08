"""Tests for CLI command handlers."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from generative_agents.backend.commands import (
    CommandAction,
    CommandResult,
    dispatch,
    get_help,
)


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_ok_returns_continue_action(self):
        result = CommandResult.ok("test output")
        assert result.output == "test output"
        assert result.action == CommandAction.CONTINUE

    def test_ok_default_empty_output(self):
        result = CommandResult.ok()
        assert result.output == ""
        assert result.action == CommandAction.CONTINUE

    def test_exit_save(self):
        result = CommandResult.exit_save("saving...")
        assert result.output == "saving..."
        assert result.action == CommandAction.EXIT_SAVE

    def test_exit_no_save(self):
        result = CommandResult.exit_no_save()
        assert result.output == ""
        assert result.action == CommandAction.EXIT_NO_SAVE

    def test_path_tester(self):
        result = CommandResult.path_tester()
        assert result.action == CommandAction.PATH_TESTER


class TestCommandRegistry:
    """Tests for CommandRegistry."""

    def test_dispatch_exact_match_save(self):
        server = MagicMock()
        result = dispatch(server, "save")
        assert result is not None
        assert result.action == CommandAction.CONTINUE
        server.save.assert_called_once()

    def test_dispatch_exact_match_case_insensitive(self):
        server = MagicMock()
        result_lower = dispatch(server, "save")
        server.reset_mock()
        result_upper = dispatch(server, "SAVE")
        assert result_lower is not None
        assert result_upper is not None
        assert result_lower.action == result_upper.action

    def test_dispatch_unknown_command_returns_none(self):
        server = MagicMock()
        result = dispatch(server, "unknown_command_xyz_123")
        assert result is None

    def test_dispatch_empty_command_returns_none(self):
        server = MagicMock()
        result = dispatch(server, "")
        assert result is None

    def test_get_help_contains_available_commands(self):
        help_text = get_help()
        assert "Available commands" in help_text
        assert "save" in help_text
        assert "run" in help_text
        assert "help" in help_text


class TestSimulationCommands:
    """Tests for simulation control commands."""

    def test_cmd_save(self):
        server = MagicMock()
        result = dispatch(server, "save")
        server.save.assert_called_once()
        assert result.action == CommandAction.CONTINUE
        assert "Saved" in result.output

    def test_cmd_fin(self):
        server = MagicMock()
        result = dispatch(server, "fin")
        server.save.assert_called_once()
        assert result.action == CommandAction.EXIT_SAVE

    def test_cmd_fin_alias_f(self):
        server = MagicMock()
        result = dispatch(server, "f")
        server.save.assert_called_once()
        assert result.action == CommandAction.EXIT_SAVE

    def test_cmd_fin_alias_finish(self):
        server = MagicMock()
        result = dispatch(server, "finish")
        server.save.assert_called_once()
        assert result.action == CommandAction.EXIT_SAVE

    def test_cmd_fin_alias_save_and_finish(self):
        server = MagicMock()
        result = dispatch(server, "save and finish")
        server.save.assert_called_once()
        assert result.action == CommandAction.EXIT_SAVE

    @patch("generative_agents.backend.commands.simulation.shutil.rmtree")
    def test_cmd_exit(self, mock_rmtree):
        server = MagicMock()
        server.sim_folder = "/tmp/test_sim"
        result = dispatch(server, "exit")
        mock_rmtree.assert_called_once_with("/tmp/test_sim")
        assert result.action == CommandAction.EXIT_NO_SAVE

    def test_cmd_run(self):
        server = MagicMock()
        result = dispatch(server, "run 100")
        server.start_server.assert_called_once_with(100)
        assert result.action == CommandAction.CONTINUE

    def test_cmd_run_different_count(self):
        server = MagicMock()
        dispatch(server, "run 500")
        server.start_server.assert_called_once_with(500)


class TestInspectionCommands:
    """Tests for inspection commands."""

    def test_cmd_print_current_time(self):
        server = MagicMock()
        server.curr_time = datetime(2023, 6, 25, 10, 30, 0)
        server.step = 42
        result = dispatch(server, "print current time")
        assert result is not None
        assert "June 25, 2023" in result.output
        assert "42" in result.output

    def test_cmd_print_persona_schedule(self):
        server = MagicMock()
        server.personas = {"Isabella Rodriguez": MagicMock()}
        server.personas[
            "Isabella Rodriguez"
        ].scratch.get_str_daily_schedule_summary.return_value = "schedule data"
        result = dispatch(server, "print persona schedule Isabella Rodriguez")
        assert result is not None
        assert "schedule data" in result.output

    def test_cmd_print_all_persona_schedule(self):
        server = MagicMock()
        persona1 = MagicMock()
        persona1.scratch.get_str_daily_schedule_summary.return_value = "schedule1"
        persona2 = MagicMock()
        persona2.scratch.get_str_daily_schedule_summary.return_value = "schedule2"
        server.personas = {"Alice": persona1, "Bob": persona2}
        result = dispatch(server, "print all persona schedule")
        assert result is not None
        assert "Alice" in result.output
        assert "Bob" in result.output
        assert "schedule1" in result.output
        assert "schedule2" in result.output

    def test_cmd_print_persona_current_tile(self):
        server = MagicMock()
        server.personas = {"Isabella Rodriguez": MagicMock()}
        server.personas["Isabella Rodriguez"].scratch.curr_tile = (50, 30)
        result = dispatch(server, "print persona current tile Isabella Rodriguez")
        assert result is not None
        assert "50" in result.output
        assert "30" in result.output

    def test_cmd_print_tile_event(self):
        server = MagicMock()
        server.maze.access_tile.return_value = {
            "events": [("test", "is", "happening", "test event")]
        }
        result = dispatch(server, "print tile event 50, 30")
        server.maze.access_tile.assert_called_once_with((50, 30))
        assert result is not None

    def test_cmd_print_tile_details(self):
        server = MagicMock()
        server.maze.access_tile.return_value = {
            "world": "test_world",
            "sector": "test_sector",
        }
        result = dispatch(server, "print tile details 50, 30")
        server.maze.access_tile.assert_called_once_with((50, 30))
        assert result is not None
        assert "world" in result.output
        assert "test_world" in result.output


class TestToolsCommands:
    """Tests for tool commands."""

    @patch("generative_agents.backend.commands.tools.shutil.rmtree")
    def test_cmd_start_path_tester_mode(self, mock_rmtree):
        server = MagicMock()
        server.sim_folder = "/tmp/test_sim"
        result = dispatch(server, "start path tester mode")
        mock_rmtree.assert_called_once_with("/tmp/test_sim")
        assert result.action == CommandAction.PATH_TESTER

    def test_cmd_call_analysis(self):
        server = MagicMock()
        server.personas = {"Isabella Rodriguez": MagicMock()}
        result = dispatch(server, "call -- analysis Isabella Rodriguez")
        server.personas[
            "Isabella Rodriguez"
        ].open_convo_session.assert_called_once_with("analysis")
        assert result.action == CommandAction.CONTINUE

    def test_cmd_help(self):
        server = MagicMock()
        result = dispatch(server, "help")
        assert result is not None
        assert "Available commands" in result.output

    def test_cmd_help_alias_question_mark(self):
        server = MagicMock()
        result = dispatch(server, "?")
        assert result is not None
        assert "Available commands" in result.output

    def test_cmd_help_alias_h(self):
        server = MagicMock()
        result = dispatch(server, "h")
        assert result is not None
        assert "Available commands" in result.output


class TestPrefixMatching:
    """Tests for prefix command matching."""

    def test_run_prefix_match(self):
        server = MagicMock()
        result = dispatch(server, "run 42")
        assert result is not None
        server.start_server.assert_called_once_with(42)

    def test_print_commands_are_prefix_matched(self):
        server = MagicMock()
        server.curr_time = datetime(2023, 1, 1, 0, 0, 0)
        server.step = 0
        # "print current time" should match even with trailing content
        result = dispatch(server, "print current time")
        assert result is not None

    def test_longest_prefix_match_wins(self):
        """Ensure 'print persona schedule' matches before 'print persona'."""
        server = MagicMock()
        server.personas = {"Test User": MagicMock()}
        server.personas[
            "Test User"
        ].scratch.get_str_daily_schedule_summary.return_value = "schedule"
        result = dispatch(server, "print persona schedule Test User")
        assert result is not None
        # Should call the schedule method, not some other print persona method
        server.personas[
            "Test User"
        ].scratch.get_str_daily_schedule_summary.assert_called_once()
