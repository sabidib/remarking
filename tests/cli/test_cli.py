import logging
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from remarking.cli import cli


def test_cli_verbosity_sets_debug(monkeypatch: MonkeyPatch) -> None:
    mock = MagicMock()
    monkeypatch.setattr(cli.logging, "basicConfig", mock)
    runner = CliRunner()
    result = runner.invoke(cli.command_line, "-vvv list")
    mock.assert_called_with(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
    assert result.exit_code == 0
    assert "Verbosity: 3" in result.output
    assert result.stderr_bytes is None


def test_cli_check_subcommands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.command_line)
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "list" in result.output
    assert "run" in result.output
    assert "persist" in result.output
    assert result.stderr_bytes is None


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.command_line, "--help")
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "list" in result.output
    assert "run" in result.output
    assert "persist" in result.output
    assert result.stderr_bytes is None


def test_cli_check_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.command_line, "--version")
    assert result.exit_code == 0
    assert ", version" in result.output


def test_cli_help_subcommand() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.command_line, "help")
    assert result.exit_code == 0
    assert "help" in result.output


def test_cli_bug() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.command_line, "bug")
    assert result.exit_code == 0
    assert "You can file a bug" in result.output
