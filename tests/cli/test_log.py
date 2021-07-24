# pylint: disable=no-self-use,missing-function-docstring
import io
import platform
import time
import typing as T

import click
import pytest
from _pytest.capture import CaptureFixture

from remarking.cli import log


def test_command_line_logger(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger()
    logger.echo("message")
    captured = capsys.readouterr()
    assert captured.out == "message\n"
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "message\n"


@pytest.mark.usefixtures("isatty")
class TestSpinnerInAtty:

    def test_spinner(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        assert "\x1b" in captured.err
        assert captured.out == ""

    def test_spinner_succeed(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        if platform.system() == "Windows":
            pytest.skip("Windows does not have halo support")
        assert "=" in captured.err
        assert "✔" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert captured.out == ""

        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed("Success")
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        if platform.system() == "Windows":
            pytest.skip("Windows does not have halo support")
        assert "=" in captured.err
        assert "✔" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert "Success" in captured.err
        assert captured.out == ""

    def test_spinner_fail(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.fail()
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        if platform.system() == "Windows":
            pytest.skip("Windows does not have halo support")
        assert "=" in captured.err
        assert "✖" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert captured.out == ""

        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.fail("Failed")
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        if platform.system() == "Windows":
            pytest.skip("Windows does not have halo support")
        assert "=" in captured.err
        assert "✖" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert "Failed" in captured.err
        assert captured.out == ""

    def test_spinner_quiet(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(quiet=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_spinner_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

    def test_spinner_disabled_shows_fail_message(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.fail("Failed")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nFailed\n"
        assert captured.out == ""

    def test_spinner_disabled_shows_succeed_message(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nSuceeded\n"
        assert captured.out == ""

    def test_spinner_quiet_and_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False, quiet=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_spinner_change_text_spinner_enabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.text = "Running"
        time.sleep(0.2)
        spinner.fail("Failed")
        captured = capsys.readouterr()

        assert "Spin" in captured.err
        if platform.system() == "Windows":
            pytest.skip("Windows does not have halo support")
        assert "=" in captured.err
        assert "✖" in captured.err
        assert "Running" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert "Failed" in captured.err
        assert captured.out == ""

    def test_spinner_change_text_spinner_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.text = "Running"
        time.sleep(0.2)
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nRunning\nSuceeded\n"
        assert captured.out == ""

    def test_spinner_does_not_write_to_file(self, capsys: CaptureFixture) -> None:
        string_io = io.StringIO()
        logger = log.CommandLineLogger(file_output=string_io)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        time.sleep(0.2)
        spinner.text = "Running"
        time.sleep(0.2)
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert "Spin" in captured.err
        assert "\x1b" in captured.err
        assert "[0m" in captured.err
        assert "Suceeded" in captured.err
        assert captured.out == ""

        assert string_io.getvalue() == ""


@pytest.mark.usefixtures("isnotatty")
class TestSpinnerNotInAtty:

    def test_spinner(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

    def test_spinner_disabled_even_when_not_tty(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

    def test_spinner_succeed(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed("Success")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nSuccess\n"
        assert captured.out == ""

    def test_spinner_fail(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger()
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.fail()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.fail("Failed")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nFailed\n"
        assert captured.out == ""

    def test_spinner_quiet(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(quiet=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_spinner_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed()
        captured = capsys.readouterr()
        assert captured.err == "Spin\n"
        assert captured.out == ""

    def test_spinner_disabled_shows_fail_message(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.fail("Failed")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nFailed\n"
        assert captured.out == ""

    def test_spinner_disabled_shows_succeed_message(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nSuceeded\n"
        assert captured.out == ""

    def test_spinner_quiet_and_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False, quiet=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_spinner_change_text_spinner_enabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=True)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.text = "Running"
        time.sleep(0.2)
        spinner.fail("Failed")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nRunning\nFailed\n"
        assert captured.out == ""

    def test_spinner_change_text_spinner_disabled(self, capsys: CaptureFixture) -> None:
        logger = log.CommandLineLogger(spinners_enabled=False)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.text = "Running"
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nRunning\nSuceeded\n"
        assert captured.out == ""

    def test_spinner_is_disabled_writing_to_file(self, capsys: CaptureFixture) -> None:
        string_io = io.StringIO()
        logger = log.CommandLineLogger(file_output=string_io)
        spinner = logger.spinner("Spin", "bouncingBar")
        spinner.start()
        spinner.text = "Running"
        spinner.succeed("Suceeded")
        captured = capsys.readouterr()
        assert captured.err == "Spin\nRunning\nSuceeded\n"
        assert captured.out == ""

        assert string_io.getvalue() == ""


def test_echo(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger()
    logger.echo("message")
    captured = capsys.readouterr()
    assert captured.out == "message\n"
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "message\n"


def test_echo_spinner_disabled(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger(spinners_enabled=False)
    logger.echo("message")
    captured = capsys.readouterr()
    assert captured.out == "message\n"
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "message\n"


def test_echo_spinner_quiet(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger(quiet=True)
    logger.echo("message")
    captured = capsys.readouterr()
    assert captured.out == ""
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == ""


def test_echo_spinner_quiet_and_spinner_disabled(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger(quiet=True, spinners_enabled=False)
    logger.echo("message")
    captured = capsys.readouterr()
    assert captured.out == ""
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == ""


def test_echo_uses_coloring_in_tty(capsys: CaptureFixture, isatty: T.Any) -> None:
    logger = log.CommandLineLogger()
    logger.echo(click.style("message", fg="red"))
    captured = capsys.readouterr()
    assert captured.out == click.style("message", fg="red") + '\n'


def test_echo_removes_coloring_when_not_in_tty(capsys: CaptureFixture, isnotatty: T.Any) -> None:
    logger = log.CommandLineLogger()
    logger.echo(click.style("message", fg="red"))
    captured = capsys.readouterr()
    assert captured.out == "message\n"


def test_echo_err(capsys: CaptureFixture) -> None:
    logger = log.CommandLineLogger()
    logger.echo("message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "message\n"


def test_echo_file(capsys: CaptureFixture) -> None:
    string_io = io.StringIO()
    logger = log.CommandLineLogger(file_output=string_io)
    logger.echo("I have a message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "I have a message\n"
    assert captured.out == ""

    assert string_io.getvalue() == ""


def test_output_result_file(capsys: CaptureFixture) -> None:
    string_io = io.StringIO()
    logger = log.CommandLineLogger(file_output=string_io)
    logger.echo("I have a message", err=True)
    captured = capsys.readouterr()
    assert captured.err == "I have a message\n"
    assert captured.out == ""
    logger.output_result("This is a result")

    assert string_io.getvalue() == "This is a result"
