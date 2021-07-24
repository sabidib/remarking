# pylint: disable=no-self-use,missing-function-docstring

from typing import List

import pytest
from click.testing import CliRunner
from pytest_unordered import unordered

from remarking import models
from remarking.cli import common
from remarking.cli import list as list_


@pytest.fixture
def highlights_with_no_documents(highlights: List[models.Highlight],
                                 highlight_4_no_corresponding_document: models.Highlight) -> List[models.Highlight]:
    return highlights + [
        highlight_4_no_corresponding_document
    ]


def test_normalize_highlights_and_documents_empty() -> None:
    normalized = common.normalize_highlights_and_documents([], [])
    assert len(normalized) == 0


def test_normalize_highlights_and_documents(
        documents: List[models.Document], highlights: List[models.Highlight]) -> None:
    normalized = common.normalize_highlights_and_documents(documents, highlights)
    assert len(normalized) > 0

    highlight_hashes = [highlight['highlight_hash'] for highlight in normalized]
    assert highlights[0].hash in highlight_hashes
    assert highlights[1].hash in highlight_hashes

    documents_with_highlights = [highlight['highlight_document_id'] for highlight in normalized]
    assert documents[0].id in documents_with_highlights
    assert documents[1].id in documents_with_highlights
    assert documents[2].id not in documents_with_highlights


def test_normalize_highlights_and_documents_highlight_with_no_matching_document(
        documents: List[models.Document], highlights_with_no_documents: List[models.Highlight]) -> None:
    with pytest.raises(common.MissingDocumentException):
        common.normalize_highlights_and_documents(documents, highlights_with_no_documents)


def test_normalize_highlights_and_documents_match_listing_columns(
        documents: List[models.Document], highlights: List[models.Highlight]) -> None:
    runner = CliRunner()
    result = runner.invoke(list_.list_, "columns")
    normalized = common.normalize_highlights_and_documents(documents, highlights)
    assert len(normalized) > 0
    keys = result.output.strip().split("\n")
    assert unordered(list(normalized[0].keys())) == keys
