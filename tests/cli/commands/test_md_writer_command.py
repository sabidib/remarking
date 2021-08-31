# pylint: disable=no-self-use,missing-function-docstring,

import typing as T
from typing import Dict, List

from _pytest.capture import CaptureFixture
from click.testing import CliRunner
import re

from remarking import models
from remarking.cli import app as app_
from remarking.cli import cli, log
from remarking.cli.commands import md_writer_command

def test_md_writer(capsys: CaptureFixture,
                      logger: log.CommandLineLogger,
                      documents: List[models.Document],
                      highlights: List[models.Highlight],
                      normalized_highlights: List[Dict[str, T.Any]]) -> None:
    md_writer = md_writer_command.MDWriter(documents, highlights, add_pages=False)
    md_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    lines = captured.out.split("\n\n")
    for line in lines:
        assert line.startswith("# ") or line.startswith("> ")

def test_md_writer_with_pages(capsys: CaptureFixture,
                      logger: log.CommandLineLogger,
                      documents: List[models.Document],
                      highlights: List[models.Highlight],
                      normalized_highlights: List[Dict[str, T.Any]]) -> None:
    md_writer = md_writer_command.MDWriter(documents, highlights, add_pages=True)
    md_writer.write(logger=logger)

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out != ""

    lines = captured.out.split("\n\n")
    for line in lines:
        if line.startswith("> "):
            m = re.search(r'\(p\. \d+\)$', line)
            assert m is not None

class TestMDWriterCommand():

    def test_run_md(self, mock_app: app_.App, normalized_highlights: List[Dict[str, T.Any]]) -> None:
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.command_line, args=["run", "md", "--token", "test", "books"])

        assert "Extractors:" in result.stderr
        assert "Collections:" in result.stderr
        assert "Connecting to RM cloud" in result.stderr

        assert normalized_highlights[0]['document_name'] in result.stdout
