# pylint: disable=no-self-use,missing-function-docstring
import datetime
from typing import List

import pytest

from remarking import models
from remarking.highlight_extractor import remarkable_highlight_extractor


@pytest.fixture
def document() -> models.Document:
    return models.Document(
        id="1c1b93ec-73db-4dcd-a24c-25971fa6346e",
        name="Through the Looking-Glass",
        current_page=16,
        bookmarked=False,
        parent="59822b79-ae2f-47f2-a15a-94426f87896f",
        version=4,
        modified_client=datetime.datetime(year=2020, month=5, day=6)
    )


@pytest.fixture
def expected_highlights(document: models.Document) -> List[models.Highlight]:
    return [
        models.Highlight.create_highlight(document.id,
                                          "\"Now, if you'll only attend, Kitty",
                                          14,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "not talk so much",
                                          14,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "What have you got to say for yourself? Now don't interrupt me!\"",
                                          12,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "Alice looked on with great interest as the King took an enorm",
                                          17,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "memorandum-book out of his pocket",
                                          17,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "The poor King looked puzzled and unhappy",
                                          17,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "\"Do you hear the snow against the window-panes Kitty? How nice and",
                                          13,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "The Queen gasped, and sat down: the rapid journey",
                                          16,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "but hug the little Lily in silence. As soon",
                                          16,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "Then she began looking about",
                                          15,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "that what could be seen from",
                                          15,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "One thing was certain, that the white kitten had had nothing to do with it:",
                                          11,
                                          "RemarkableHighlightExtractor"),
        models.Highlight.create_highlight(document.id,
                                          "The way Dinah washed her children's faces was this",
                                          11,
                                          "RemarkableHighlightExtractor")
    ]


@pytest.fixture
def test1_path() -> str:
    return "tests/data/highlights/remarkable_highlight_extractor/test_1"


@pytest.fixture
def test2_path() -> str:
    return "tests/data/highlights/remarkable_highlight_extractor/test_2"


def compare_highlights(highlights_1: List[models.Highlight], highlights_2: List[models.Highlight]) -> None:
    highlight_1_list = sorted(highlights_1[:], key=lambda x: x.page_number)
    highlight_2_list = sorted(highlights_2[:], key=lambda x: x.page_number)
    for highlight_1, highlight_2 in zip(highlight_1_list, highlight_2_list):
        assert highlight_1.equal(highlight_2)


def test_extractor(test1_path: str,
                   document: models.Document,
                   expected_highlights: List[models.Highlight]) -> None:
    extractor = remarkable_highlight_extractor.RemarkableHighlightExtractor()
    highlights = extractor.get_highlights(test1_path, document)
    compare_highlights(highlights, expected_highlights)


def test_extractor_returns_nothing_for_no_highlights(test2_path: str,
                                                     document: models.Document,
                                                     expected_highlights: List[models.Highlight]) -> None:
    extractor = remarkable_highlight_extractor.RemarkableHighlightExtractor()
    assert extractor.get_highlights(test2_path, document) == []
