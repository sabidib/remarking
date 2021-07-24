# pylint: disable=no-self-use,missing-function-docstring,

import io
import json
from typing import List

from _pytest.capture import CaptureFixture
from click.testing import CliRunner

from remarking import models
from remarking.cli import app as app_
from remarking.cli import cli, log
from remarking.cli.commands import json_writer_command


def test_json_writer(capsys: CaptureFixture,
                     logger: log.CommandLineLogger,
                     documents: List[models.Document],
                     highlights: List[models.Highlight]) -> None:
    json_writer = json_writer_command.JSONWriter(documents, highlights)
    json_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    loaded = json.loads(captured.out)

    assert len(loaded['documents']) > 0
    assert len(loaded['highlights']) > 0
    found_highlights = [
        highlight for highlight in loaded['highlights'] if highlight['hash'] == highlights[0].hash
    ]
    assert len(found_highlights) == 1
    assert found_highlights[0]['text'] == highlights[0].text


def test_json_writer_writes_unix_timestamp(capsys: CaptureFixture,
                                           logger: log.CommandLineLogger,
                                           documents: List[models.Document],
                                           highlights: List[models.Highlight]) -> None:
    json_writer = json_writer_command.JSONWriter(documents, highlights)
    json_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    loaded = json.loads(captured.out)

    assert len(loaded['highlights']) > 0
    assert isinstance(loaded['highlights'][0]['extracted_at'], int)
    assert loaded['highlights'][0]['extracted_at'] > 0


def test_json_writer_file(capsys: CaptureFixture,
                          documents: List[models.Document],
                          highlights: List[models.Highlight]) -> None:
    string_io = io.StringIO()
    logger = log.CommandLineLogger(file_output=string_io)
    json_writer = json_writer_command.JSONWriter(documents, highlights)
    json_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    loaded = json.loads(string_io.getvalue())
    assert len(loaded['documents']) > 0
    assert len(loaded['highlights']) > 0
    found_highlights = [
        highlight for highlight in loaded['highlights'] if highlight['hash'] == highlights[0].hash
    ]
    assert len(found_highlights) == 1
    assert found_highlights[0]['text'] == highlights[0].text


def test_json_writer_empty(capsys: CaptureFixture,
                           logger: log.CommandLineLogger,
                           documents: List[models.Document],
                           highlights: List[models.Highlight]) -> None:
    json_writer = json_writer_command.JSONWriter([], [])
    json_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    loaded = json.loads(captured.out)

    assert len(loaded['documents']) == 0
    assert len(loaded['highlights']) == 0


class TestJSONWriterCommand():

    def test_run_json(self, mock_app: app_.App) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line, args=["run", "json", "--token", "test_token", "books"])

        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr
        assert json.loads(result.stdout)
