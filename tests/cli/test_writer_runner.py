# pylint: disable=no-self-use,missing-function-docstring

from typing import Iterator, List
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from remarking import rmcloud as rmcloud_
from remarking.cli import app as app_
from remarking.cli import cli, writer_command_runner


def test_token_prompting_when_not_authed(mock_app: app_.App,
                                         monkeypatch: MonkeyPatch,
                                         isatty: Iterator[None],
                                         cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock(side_effect=[rmcloud_.AuthError, None])
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"], input="test_token")
    assert result.exit_code == 0
    assert "Enter your one-time auth token from" in result.stderr
    assert "my.remarkable.com" in result.stderr

    assert "{\"documen" in result.stdout


def test_token_prompting_does_not_prompt_if_already_authed(mock_app: app_.App,
                                                           monkeypatch: MonkeyPatch,
                                                           isatty: Iterator[None],
                                                           cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock()
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"], input="test_token")
    assert result.exit_code == 0
    assert "Enter your one-time auth token from" not in result.stderr
    assert "my.remarkable.com" not in result.stderr

    assert "{\"documen" in result.stdout


def test_token_prompting_prints_warning_when_renewal_fails(mock_app: app_.App,
                                                           monkeypatch: MonkeyPatch,
                                                           isatty: Iterator[None],
                                                           cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock(side_effect=[rmcloud_.RenewAuthError, None])
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"], input="test_token")
    assert result.exit_code == 0
    assert "Failed to renew auth for reMarkable cloud. Did you de-authorize remarking?" in result.stderr
    assert "Enter your one-time auth token from" in result.stderr
    assert "my.remarkable.com" in result.stderr
    assert "{\"documen" in result.stdout


def test_token_prompting_when_is_atty(mock_app: app_.App,
                                      monkeypatch: MonkeyPatch,
                                      isatty: Iterator[None],
                                      cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock(side_effect=[rmcloud_.AuthError, None])
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"], input="test_token")
    assert result.exit_code == 0
    assert "Enter your one-time auth token from" in result.stderr
    assert "my.remarkable.com" in result.stderr

    assert "{\"documen" in result.stdout


def test_token_prompting_fails_when_not_atty(mock_app: app_.App,
                                             monkeypatch: MonkeyPatch,
                                             isnotatty: Iterator[None],
                                             cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock(side_effect=rmcloud_.AuthError)
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"])
    assert result.exit_code == 2
    assert "Missing option '-t'" in result.stderr
    assert "Are you in non-interactive" in result.stderr
    assert "piping" in result.stderr


def test_token_prompting_does_not_run_when_authed_and_when_not_atty(mock_app: app_.App,
                                                                    monkeypatch: MonkeyPatch,
                                                                    isnotatty: Iterator[None],
                                                                    cmd_start: List[str]) -> None:
    mock_rmcloud = MagicMock()
    monkeypatch.setattr(writer_command_runner.rmcloud_, "RMCloud", mock_rmcloud)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.command_line, args=cmd_start + ["books"])
    assert result.exit_code == 0
    assert "Missing option '-t'" not in result.stderr
    assert "Are you in non-interactive" not in result.stderr
    assert "piping" not in result.stderr
