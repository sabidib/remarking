
from click.testing import CliRunner
from rmapy import document as document_

from remarking import models
from remarking.cli import common
from remarking.cli import list as list_


def test_list_command() -> None:
    runner = CliRunner()
    result = runner.invoke(list_.list_)
    assert result.exit_code == 0
    assert "List" in result.output
    assert "List useful information" in result.output
    assert result.stderr_bytes is None


def test_extractors_command() -> None:
    runner = CliRunner()
    result = runner.invoke(list_.list_, "extractors")
    assert result.exit_code == 0
    for key in common.get_extractor_mappings().keys():
        assert key in result.output
    assert "====" in result.output
    assert result.stderr_bytes is None


def test_columns_command(rmapy_document: document_.Document) -> None:
    runner = CliRunner()
    result = runner.invoke(list_.list_, "columns")
    assert result.exit_code == 0
    highlight_keys = models.Highlight.create_highlight(
        "834834",
        "text",
        1,
        "unextracted"
    ).to_dict().keys()

    document_keys = models.Document.from_cloud_document(rmapy_document).to_dict().keys()

    for key in (*highlight_keys, *document_keys):
        assert key + "\n" in result.output
    assert result.stderr_bytes is None
