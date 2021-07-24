# pylint: disable=no-self-use,missing-function-docstring,

import typing as T
from typing import Dict, List

from _pytest.capture import CaptureFixture
from click.testing import CliRunner

from remarking import models
from remarking.cli import app as app_
from remarking.cli import cli, log
from remarking.cli.commands import table_writer_command


def test_table_writer(capsys: CaptureFixture,
                      logger: log.CommandLineLogger,
                      documents: List[models.Document],
                      highlights: List[models.Highlight],
                      normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = table_writer_command.TableWriter(documents, highlights)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""
    assert "-----" in captured.out
    assert "..." in captured.out

    headers = captured.out.split("\n")[0]
    for key in list(normalized_highlights[0].keys()):
        assert key in headers

    assert highlights[0].hash in captured.out


def test_table_writer_no_truncate(capsys: CaptureFixture,
                                  logger: log.CommandLineLogger,
                                  documents: List[models.Document],
                                  highlights: List[models.Highlight],
                                  normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = table_writer_command.TableWriter(documents, highlights, truncate=False)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""
    assert "-----" in captured.out
    assert "..." not in captured.out

    headers = captured.out.split("\n")[0]
    for key in list(normalized_highlights[0].keys()):
        assert key in headers

    assert highlights[0].hash in captured.out


def test_table_writer_columns(capsys: CaptureFixture,
                              logger: log.CommandLineLogger,
                              documents: List[models.Document],
                              highlights: List[models.Highlight],
                              normalized_highlights: List[Dict[str, T.Any]]) -> None:
    columns = ["highlight_hash", "document_name", "highlight_text", "highlight_page_number"]
    csv_writer = table_writer_command.TableWriter(documents, highlights, columns=columns)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    headers = captured.out.split("\n")[0]

    keys = list(normalized_highlights[0].keys())
    for column in columns:
        keys.remove(column)

    for key in columns:
        assert key in headers

    for key in keys:
        assert key not in headers

    assert highlights[0].hash in captured.out


def test_table_writer_empty(capsys: CaptureFixture, logger: log.CommandLineLogger) -> None:
    csv_writer = table_writer_command.TableWriter([], [])
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""


def test_table_writer_plain(capsys: CaptureFixture,
                            logger: log.CommandLineLogger,
                            documents: List[models.Document],
                            highlights: List[models.Highlight],
                            normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = table_writer_command.TableWriter(documents, highlights, print_plain=True)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    assert "-----" not in captured.out

    headers = captured.out.split("\n")[0]
    for key in list(normalized_highlights[0].keys()):
        assert key in headers

    assert highlights[0].hash in captured.out


def test_table_writer_plain_no_truncate(capsys: CaptureFixture,
                                        logger: log.CommandLineLogger,
                                        documents: List[models.Document],
                                        highlights: List[models.Highlight],
                                        normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = table_writer_command.TableWriter(documents, highlights, print_plain=True)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    assert "-----" not in captured.out
    assert "..." not in captured.out

    headers = captured.out.split("\n")[0]
    for key in list(normalized_highlights[0].keys()):
        assert key in headers

    assert highlights[0].hash in captured.out


def test_table_writer_plain_empty(capsys: CaptureFixture, logger: log.CommandLineLogger) -> None:
    csv_writer = table_writer_command.TableWriter([], [], print_plain=True)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""


# TODO: refactor table and table writer into table based output writer
class TestTableWriterCommand():

    def test_run_table(self, mock_app: app_.App, normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line, args=["run", "table", "--token", "test", "books"])

        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

        assert normalized_highlights[0]['document_name'] in result.stdout

    def test_column_parser(self, mock_app: app_.App, normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line,
                               args=["run",
                                     "table",
                                     "--columns",
                                     "document_name,highlight_text",
                                     "--token",
                                     "test",
                                     "books"])

        assert result.exit_code == 0
        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

        assert "a_book" in result.stdout
        assert "document_name" in result.stdout
        assert "highlight_text" in result.stdout
        assert normalized_highlights[0]['highlight_text'] in result.stdout
        assert normalized_highlights[0]['highlight_hash'] not in result.stdout

    def test_columns_are_validated(self, mock_app: app_.App) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line,
                               args=["run",
                                     "table",
                                     "--columns",
                                     "document_name,highlight_text,nope",
                                     "--token",
                                     "test",
                                     "books"])
        assert result.exit_code == 2
        assert "document_id" in result.stderr
