# pylint: disable=no-self-use,missing-function-docstring

import json
import pathlib
from typing import Iterator, List
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from remarking.cli import app as app_
from remarking.cli import cli, extract


def verify_output_is_valid_json(stdout: str) -> None:
    try:
        assert json.loads(stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            "Failed to parse stdout of run command as json. "
            "Either the json is broken or something other than the output is being printed to stdout"
            "\nException: " + str(exc)
        )


def test_run_command(mock_app: app_.App) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=["run", "json", "--token", "test", "books"])
    assert result.exit_code == 0

    verify_output_is_valid_json(result.stdout)

    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr


def test_persist_command(mock_app: app_.App) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli.command_line,
        args=[
            "persist",
            "--sqlalchemy",
            "dne",
            "json",
            "--token",
            "test",
            "books"])
    assert result.exit_code == 0

    verify_output_is_valid_json(result.stdout)

    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr

def test_persist_command_sqlalchemy_environment(mock_app: app_.App) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli.command_line,
        args=[
            "persist",
            "json",
            "--token",
            "test",
            "books"],
        env={
            "REMARKING_SQLALCHEMY": "dne"
        }
    )
    assert result.exit_code == 0

    verify_output_is_valid_json(result.stdout)

    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr




def test_persist_command_accepts_file_name(mock_app: app_.App, tmpdir: pathlib.Path) -> None:
    runner = CliRunner(mix_stderr=False)
    file = tmpdir / "my_secret_file.conf"
    db_path = tmpdir / "test_db.1"

    with open(file, "w") as file_p:
        file_p.write(f"sqlite://{db_path}")

    result = runner.invoke(
        cli.command_line,
        args=[
            "persist",
            "--sqlalchemy",
            str(file),
            "json",
            "--token",
            "test",
            "books"])
    assert result.exit_code == 0

    verify_output_is_valid_json(result.stdout)

    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr


def test_run_help(mock_app: app_.App) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=["run", "--help"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert "run [OPTIONS]" in result.stdout
    assert "Show this message and exit" in result.stdout


def test_persist_help(mock_app: app_.App) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=["persist", "--sqlalchemy", "dne", "--help"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert "persist [OPTIONS]" in result.stdout
    assert "Show this message and exit" in result.stdout


def test_persist_sqlalchemy_command_has_default(mock_app: app_.App, tmpdir: pathlib.Path) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=["persist", "json", "--token", "test", "books"])
    assert result.exit_code == 0
    assert result.stdout != ""
    assert result.stderr != ""


def test_invalid_token(monkeypatch: MonkeyPatch, mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    mock_rmcloud = MagicMock(side_effect=extract.rmcloud_.AuthError)
    monkeypatch.setattr(extract.rmcloud_, "RMCloud", mock_rmcloud)
    result = runner.invoke(cli.command_line, args=cmd_start + ["--token", "nope", "books"])
    assert result.exit_code == 1
    assert "Failed to connect to the Remarkable Cloud" in result.stdout

    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr


def test_invalid_extractor(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli.command_line,
        args=cmd_start + [
            "--token",
            "test",
            "--extractors",
            "invalid",
            "books"])
    assert result.exit_code == 2
    assert "'invalid' is not in list of extractors" in result.stderr
    assert result.stdout == ""


def test_extractor_parser(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli.command_line,
        args=cmd_start + [
            "--token",
            "test",
            "--extractors",
            "invalid",
            "books"])
    assert result.exit_code == 2
    assert "'invalid' is not in list of extractors" in result.stderr
    assert result.stdout == ""


def test_extractor_names_are_validated(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli.command_line,
        args=cmd_start + [
            "--token",
            "test",
            "--extractors",
            "remarkable, invalid",
            "books"])
    assert result.exit_code == 2
    assert "'invalid' is not in list of extractors" in result.stderr
    assert result.stdout == ""


def test_logging_when_redirecting_stdout(mock_app: app_.App, isnotatty: Iterator[None], cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["--token", "test", "books"])
    assert result.exit_code == 0
    assert result.stdout != ""


def test_logging_when_redirecting_stderr(mock_app: app_.App, isnotatty: Iterator[None], cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["--token", "test", "books"])
    assert result.exit_code == 0
    assert result.stdout != ""


def test_logging_when_tty(mock_app: app_.App, isatty: Iterator[None], cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=True)
    result = runner.invoke(cli.command_line, args=cmd_start + ["--token", "test", "books"])
    assert result.exit_code == 0
    assert "1m\x1b[36m" in result.stdout
    assert "Extractors:" in result.stdout
    assert "Collections:" in result.stdout
    assert "Connecting to RM cloud" in result.stdout


def test_logging_when_quiet(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(cli.command_line, args=cmd_start + ["--token", "test", "books", "-q"])
    assert result.exit_code == 0
    assert result.stderr == ""
    verify_output_is_valid_json(result.stdout)


def test_logging_debug_applied(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(cli.command_line, args=["-vvv", "run", "json", "--token", "test", "books"])
    assert result.exit_code == 0
    assert result.stderr != ""
    verify_output_is_valid_json(result.stdout)
    assert "1m\x1b[36m" not in result.stderr
    assert "Verbosity:" in result.stderr
    assert "Extractors:" in result.stderr
    assert "Collections:" in result.stderr
    assert "Connecting to RM cloud" in result.stderr


def test_logging_when_output_to_file(mock_app: app_.App, tmpdir: pathlib.Path, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(cli.command_line,
                           args=["-vvv",
                                 ] + cmd_start + [
                               "--token",
                               "test",
                               "-o",
                               str(tmpdir / "my_file.json"), "books"])
    assert result.exit_code == 0
    with open(tmpdir / "my_file.json", "r") as file:
        verify_output_is_valid_json(file.read())
    assert "Verbosity:" in result.stderr


def test_working_directory_is_validated(mock_app: app_.App, tmpdir: pathlib.Path, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line,
                           args=cmd_start + [
                               "json",
                               "--token",
                               "test",
                               "--working-directory",
                               str(tmpdir) + "/dne",
                               "books"])
    assert result.exit_code == 0
    verify_output_is_valid_json(result.stdout)


def test_working_already_exists(mock_app: app_.App, tmpdir: pathlib.Path, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line,
                           args=cmd_start + [
                               "--token",
                               "token",
                               "--working-directory",
                               str(tmpdir),
                               "books"])
    assert result.exit_code == 0
    verify_output_is_valid_json(result.stdout)


def test_run_lists_warning_on_empty_collection_names(mock_app: app_.App, cmd_start: List[str]) -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line,
                           args=cmd_start + [
                               "--token",
                               "token",
                           ])
    assert result.exit_code == 0
    assert "Empty list of collection names" in result.stderr
