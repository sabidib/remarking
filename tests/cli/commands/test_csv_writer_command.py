# pylint: disable=no-self-use,missing-function-docstring
import csv
import io
import typing as T
from typing import Dict, List

from _pytest.capture import CaptureFixture
from click.testing import CliRunner
from pytest_unordered import unordered

from remarking import models
from remarking.cli import app as app_
from remarking.cli import cli, log
from remarking.cli.commands import csv_writer_command


def test_csv_writer(capsys: CaptureFixture,
                    logger: log.CommandLineLogger,
                    documents: List[models.Document],
                    highlights: List[models.Highlight],
                    normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = csv_writer_command.CSVWriter(documents, highlights)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    string_io = io.StringIO(newline='')
    string_io.write(captured.out)
    string_io.seek(0)
    reader = csv.reader(string_io, delimiter=csv_writer.delimiter)
    rows = list(reader)
    assert unordered(rows[0]) == list(normalized_highlights[0].keys())

    indexes_found = [index for index, key in enumerate(rows[0]) if key == "highlight_hash"]
    assert len(indexes_found) == 1
    index = indexes_found[0]

    found_rows = [row for row in rows if row[index] == highlights[0].hash]
    assert len(found_rows) == 1


def test_csv_writer_delimiter(capsys: CaptureFixture,
                              logger: log.CommandLineLogger,
                              documents: List[models.Document],
                              highlights: List[models.Highlight],
                              normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = csv_writer_command.CSVWriter(documents, highlights, delimiter="|")
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    string_io = io.StringIO(newline='')
    string_io.write(captured.out)
    string_io.seek(0)
    reader = csv.reader(string_io, delimiter=csv_writer.delimiter)
    rows = list(reader)
    assert unordered(rows[0]) == list(normalized_highlights[0].keys())

    indexes_found = [index for index, key in enumerate(rows[0]) if key == "highlight_hash"]
    assert len(indexes_found) == 1
    index = indexes_found[0]

    found_rows = [row for row in rows if row[index] == highlights[0].hash]
    assert len(found_rows) == 1


def test_csv_writer_empty(capsys: CaptureFixture,
                          logger: log.CommandLineLogger,
                          documents: List[models.Document],
                          highlights: List[models.Highlight],
                          normalized_highlights: List[Dict[str, T.Any]]) -> None:
    csv_writer = csv_writer_command.CSVWriter([], [])
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    string_io = io.StringIO(newline='')
    string_io.write(captured.out)
    string_io.seek(0)
    reader = csv.reader(string_io, delimiter=csv_writer.delimiter)
    rows = list(reader)
    assert unordered(rows[0]) == list(normalized_highlights[0].keys())

    indexes_found = [index for index, key in enumerate(rows[0]) if key == "highlight_hash"]
    assert len(indexes_found) == 1


def test_csv_writer_columns(capsys: CaptureFixture,
                            logger: log.CommandLineLogger,
                            documents: List[models.Document],
                            highlights: List[models.Highlight],
                            normalized_highlights: List[Dict[str, T.Any]]) -> None:
    columns = ["highlight_hash", "document_name", "highlight_text"]
    csv_writer = csv_writer_command.CSVWriter(documents, highlights, columns=columns)
    csv_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""

    string_io = io.StringIO(newline='')
    string_io.write(captured.out)
    string_io.seek(0)
    reader = csv.reader(string_io, delimiter=csv_writer.delimiter)
    rows = list(reader)
    assert unordered(rows[0]) == columns

    indexes_found = [index for index, key in enumerate(rows[0]) if key == "highlight_hash"]
    assert len(indexes_found) == 1
    index = indexes_found[0]

    found_rows = [row for row in rows if row[index] == highlights[0].hash]
    assert len(found_rows) == 1


class TestCSVWriterCommand():

    def test_run_csv(self,
                     mock_app: app_.App,
                     normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line, args=["run", "csv", "--token", "test", "books"])
        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

        string_io = io.StringIO(newline='')
        string_io.write(result.stdout)
        string_io.seek(0)
        reader = csv.reader(string_io, delimiter=",")
        rows = list(reader)
        assert [row_header in list(normalized_highlights[0].keys()) for row_header in rows[0]]

    def test_run_csv_delimieter(self,
                                mock_app: app_.App,
                                normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line, args=["run", "csv", "--token", "test", "--delimiter", "|", "books"])
        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

        string_io = io.StringIO(newline='')
        string_io.write(result.stdout)
        string_io.seek(0)
        reader = csv.reader(string_io, delimiter="|")
        rows = list(reader)
        assert [row_header in list(normalized_highlights[0].keys()) for row_header in rows[0]]

    def test_column_parser(self,
                           mock_app: app_.App,
                           normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line,
                               args=["run",
                                     "csv",
                                     "--columns",
                                     "document_name,highlight_text,highlight_page_number",
                                     "--token",
                                     "test_token",
                                     "books"])

        string_io = io.StringIO(newline='')
        string_io.write(result.stdout)
        string_io.seek(0)
        reader = csv.reader(string_io, delimiter=",")
        rows = list(reader)
        assert unordered(rows[0]) == ["document_name", "highlight_text", "highlight_page_number"]
        assert result.exit_code == 0
        assert "a_book" in result.stdout
        assert "document_name" in result.stdout
        assert "highlight_page_number" in result.stdout
        assert "highlight_text" in result.stdout
        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

    def test_columns_are_validated(self,
                                   mock_app: app_.App) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line,
                               args=["run",
                                     "csv",
                                     "--columns",
                                     "document_name,highlight_text,dne",
                                     "--token",
                                     "test",
                                     "books"])
        assert "," in result.stderr
        assert result.exit_code == 2
        assert "document_id" in result.stderr
