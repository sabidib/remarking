# pylint: disable=no-self-use,missing-function-docstring
import datetime
import itertools
from typing import Dict, Iterator, List
from unittest.mock import MagicMock

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from pytest_unordered import unordered
from rmapy import collections as collections_
from rmapy import document as document_

from remarking import models
from remarking import rmcloud as rmcloud_
from remarking.cli import app as app_
from remarking.cli import log
from remarking.highlight_extractor import highlight_extractor
from remarking.storage import sqlalchemy_storage as sqlalchemy_storage_


class MockExtractor(highlight_extractor.HighlightExtractor):
    """ Mock extractor """

    def __init__(self, highlights: List[models.Highlight]) -> None:
        self.documents_to_highlights: Dict[str, List[models.Highlight]] = {}
        self.was_called = False
        for highlight in highlights:
            self.add_highlight(highlight)

    @classmethod
    def get_extractor_instance_data(cls) -> List[highlight_extractor.ExtractorData]:
        return [
            highlight_extractor.ExtractorData(
                extractor_name="mock_extractor",
                instance=cls([]),
                description=cls.__doc__
            )
        ]

    def add_highlight(self, highlight: models.Highlight) -> None:
        if highlight.document_id not in self.documents_to_highlights:
            self.documents_to_highlights[highlight.document_id] = []

        self.documents_to_highlights[highlight.document_id].append(highlight)

    def get_highlights(self, working_path: str, document: models.Document) -> List[models.Highlight]:
        self.was_called = True
        if document.id not in self.documents_to_highlights:
            return []
        highlights = self.documents_to_highlights[document.id]
        return list(itertools.chain(*[highlights]))


@pytest.fixture
def rmcloud(monkeypatch: MonkeyPatch,
            rmapy_collection: collections_.Collection,
            mock_rmcloud: rmcloud_.RMCloud) -> Iterator[rmcloud_.RMCloud]:
    cloud = rmcloud_.RMCloud("token")
    cloud.download_document = MagicMock()  # type: ignore
    yield cloud


@pytest.fixture
def mock_extractor(highlights: List[models.Highlight]) -> MockExtractor:
    return MockExtractor(highlights)


@pytest.fixture
def extractors(mock_extractor: MockExtractor) -> List[MockExtractor]:
    return [mock_extractor]


def add_new_highlight(extractor: MockExtractor, highlight: models.Highlight) -> None:
    extractor.add_highlight(highlight)


def update_document_modified_at_and_store(rmcloud_obj: rmcloud_.RMCloud, document: models.Document) -> None:
    current_collection = rmcloud_obj._api_client.get_meta_items()  # pylint: disable=protected-access
    for item in current_collection:
        if item.ID == document.id:
            item.ModifiedClient = datetime.datetime.now().isoformat()
            break


def add_new_document_and_store_in_cloud(rmcloud_obj: rmcloud_.RMCloud, document: document_.Document) -> None:
    current_collection = rmcloud_obj._api_client.get_meta_items()  # pylint: disable=protected-access
    current_collection.add(document.to_dict())


def verify_highlights(highlights_list_entered: List[models.Highlight],
                      highlights_from_app: List[models.Highlight]) -> None:
    deduped_highlights_ids = set()

    for highlight in highlights_list_entered:
        if highlight.hash not in deduped_highlights_ids:
            deduped_highlights_ids.add(highlight.hash)

    assert unordered(list(deduped_highlights_ids)) == [highlight.hash for highlight in highlights_from_app]


def verify_documents(documents: List[models.Document], documents_from_app: List[models.Document]) -> None:
    assert unordered([doc.id for doc in documents if doc.id != "33333"]) == [doc.id for doc in documents_from_app]


def test_app(rmcloud: rmcloud_.RMCloud,
             logger: log.CommandLineLogger,
             extractors: List[highlight_extractor.HighlightExtractor],
             sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
             documents: List[models.Document],
             highlights: List[models.Highlight],
             capsys: CaptureFixture) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    assert len(new_highlights) > 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)


def test_app_no_logger(rmcloud: rmcloud_.RMCloud,
                       logger: log.CommandLineLogger,
                       extractors: List[highlight_extractor.HighlightExtractor],
                       sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                       documents: List[models.Document],
                       highlights: List[models.Highlight],
                       capsys: CaptureFixture) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)


def test_app_no_storage(rmcloud: rmcloud_.RMCloud,
                        logger: log.CommandLineLogger,
                        extractors: List[highlight_extractor.HighlightExtractor],
                        sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                        documents: List[models.Document],
                        highlights: List[models.Highlight],
                        capsys: CaptureFixture) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)


def test_app_prints_nothing_when_logger_quiet(rmcloud: rmcloud_.RMCloud,
                                              logger: log.CommandLineLogger,
                                              extractors: List[highlight_extractor.HighlightExtractor],
                                              sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                              documents: List[models.Document],
                                              highlights: List[models.Highlight],
                                              capsys: CaptureFixture) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=log.CommandLineLogger(quiet=True))
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)


def test_app_run_empty_collection_name(rmcloud: rmcloud_.RMCloud,
                                       logger: log.CommandLineLogger,
                                       extractors: List[highlight_extractor.HighlightExtractor],
                                       sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                       documents: List[models.Document],
                                       highlights: List[models.Highlight],
                                       capsys: CaptureFixture
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", [])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) == 0
    assert len(new_documents) == 0


def test_app_run_invalid_collection_names(rmcloud: rmcloud_.RMCloud,
                                          logger: log.CommandLineLogger,
                                          extractors: List[highlight_extractor.HighlightExtractor],
                                          sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                          documents: List[models.Document],
                                          highlights: List[models.Highlight],
                                          capsys: CaptureFixture
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["does_not_exist"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) == 0
    assert len(new_documents) == 0


@pytest.mark.skip()
def test_app_run_invalid_path(rmcloud: rmcloud_.RMCloud,
                              logger: log.CommandLineLogger,
                              extractors: List[highlight_extractor.HighlightExtractor],
                              sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                              documents: List[models.Document],
                              highlights: List[models.Highlight],
                              capsys: CaptureFixture
) -> None:
    pass


def test_app_downloads(rmcloud: rmcloud_.RMCloud,
                       logger: log.CommandLineLogger,
                       extractors: List[highlight_extractor.HighlightExtractor],
                       sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                       documents: List[models.Document],
                       highlights: List[models.Highlight],
                       capsys: CaptureFixture
                       ) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    path = "tmp/434325"
    new_documents, new_highlights = app.run_app(path, ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0
    rmcloud.download_document.assert_any_call(documents[1].id, path)  # type: ignore
    assert rmcloud.download_document.call_count == 3  # type: ignore


def test_app_uses_passed_collection_names(rmcloud: rmcloud_.RMCloud,
                                          logger: log.CommandLineLogger,
                                          extractors: List[highlight_extractor.HighlightExtractor],
                                          sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                          documents: List[models.Document],
                                          highlights: List[models.Highlight],
                                          capsys: CaptureFixture
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder_2"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) == 1
    assert new_documents[0].id == "22222"


def test_app_run_runs_extractors(rmcloud: rmcloud_.RMCloud,
                                 logger: log.CommandLineLogger,
                                 extractors: List[highlight_extractor.HighlightExtractor],
                                 sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                 documents: List[models.Document],
                                 highlights: List[models.Highlight],
                                 capsys: CaptureFixture,
                                 mock_extractor: highlight_extractor.HighlightExtractor
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert mock_extractor.was_called
    assert len(new_highlights) > 0
    assert len(new_documents) > 0


def test_app_run_saves_to_storage(rmcloud: rmcloud_.RMCloud,
                                  logger: log.CommandLineLogger,
                                  extractors: List[highlight_extractor.HighlightExtractor],
                                  sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                  documents: List[models.Document],
                                  highlights: List[models.Highlight],
                                  capsys: CaptureFixture,
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0

    stored_documents = sqlalchemy_storage.get_documents()
    stored_highlights = sqlalchemy_storage.get_highlights()

    # Should not contain "33333" as there are no associated highlights for it.
    assert unordered(doc.id for doc in new_documents) == [doc.id for doc in stored_documents if doc.id != "33333"]
    assert unordered(highlight.hash for highlight in new_highlights) == [
        highlight.hash for highlight in stored_highlights]

    # should have all documents
    assert unordered(doc.id for doc in stored_documents) == [doc.id for doc in documents]


def test_app_run_prints_extractor_running(rmcloud: rmcloud_.RMCloud,
                                          logger: log.CommandLineLogger,
                                          extractors: List[highlight_extractor.HighlightExtractor],
                                          sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                          documents: List[models.Document],
                                          highlights: List[models.Highlight],
                                          capsys: CaptureFixture,
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0
    assert "Running extractors on documents" in captured.err
    assert "MockExtractor" in captured.err
    assert f"on \"{documents[1].name}\"" in captured.err
    assert f"found {len(new_highlights)} highlights, {len(new_highlights)} are new." in captured.err


def test_app_run_prints_downloading_doc(rmcloud: rmcloud_.RMCloud,
                                        logger: log.CommandLineLogger,
                                        extractors: List[highlight_extractor.HighlightExtractor],
                                        sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                        documents: List[models.Document],
                                        highlights: List[models.Highlight],
                                        capsys: CaptureFixture,
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0
    assert "Downloading documents" in captured.err
    assert f"Downloading \"{documents[1].name}\"" in captured.err


def test_app_run_returns_documents_sorted_by_name(rmcloud: rmcloud_.RMCloud,
                                                  logger: log.CommandLineLogger,
                                                  extractors: List[highlight_extractor.HighlightExtractor],
                                                  sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                                                  documents: List[models.Document],
                                                  highlights: List[models.Highlight],
                                                  capsys: CaptureFixture,
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0
    assert [
        doc.id for doc in sorted((doc for doc in documents if doc.id != "33333"), key=lambda x: x.name)
    ] == [doc.id for doc in new_documents]


def test_app_run_returns_highlights_sorted_by_doc_name_and_page_number(
        rmcloud: rmcloud_.RMCloud,
        logger: log.CommandLineLogger,
        extractors: List[highlight_extractor.HighlightExtractor],
        sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
        documents: List[models.Document],
        highlights: List[models.Highlight],
        capsys: CaptureFixture) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_highlights) > 0
    assert len(new_documents) > 0
    highlights_by_doc = []
    for doc in new_documents:
        highlights_by_doc.append([highlight for highlight in highlights if highlight.document_id == doc.id])

    for highlights_in_doc in highlights_by_doc:
        highlights_in_doc.sort(key=lambda x: x.page_number)

    sorted_highlights = [highlights.hash for highlights in itertools.chain(*
                                                                           highlights_by_doc
    )]

    # remove duplicate
    # py3 preserves dictionary order
    sorted_highlights = list(dict.fromkeys(sorted_highlights))

    assert sorted_highlights == [highlight.hash for highlight in new_highlights]


def test_app_run_no_persist_returns_all_highlights(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    # nothing changes
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    # nothing changes
    document_for_new_highlight = new_documents[0]
    new_highlight = models.Highlight.create_highlight(
        document_for_new_highlight.id,
        "new_text",
        20,
        "manually added"
    )

    # We don't update the document because this is a non-persisted run.
    # update_document_modified_at_and_store(rmcloud, document_for_new_highlight)

    add_new_highlight(mock_extractor, new_highlight)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights + [new_highlight], new_highlights)
    verify_documents(documents, new_documents)


def test_app_run_persist_returns_nothing_if_nothing_updated(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor,
    rmapy_document_new: document_.Document
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights([], new_highlights)
    verify_documents([], new_documents)


def test_app_run_persist_returns_new_highlights_for_modified_document(
        rmcloud: rmcloud_.RMCloud,
        logger: log.CommandLineLogger,
        extractors: List[highlight_extractor.HighlightExtractor],
        sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
        documents: List[models.Document],
        highlights: List[models.Highlight],
        capsys: CaptureFixture,
        mock_extractor: highlight_extractor.HighlightExtractor) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    # add new highlight existing document
    document_for_new_highlight = new_documents[0]
    new_highlight = models.Highlight.create_highlight(
        document_for_new_highlight.id,
        "new_text",
        20,
        "manually added"
    )
    update_document_modified_at_and_store(rmcloud, document_for_new_highlight)
    add_new_highlight(mock_extractor, new_highlight)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights([new_highlight], new_highlights)
    verify_documents([document_for_new_highlight], new_documents)


def test_app_run_persist_returns_highlights_for_new_documents(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor,
    rmapy_document_new: document_.Document
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)
    # add new document with a new highlight
    add_new_document_and_store_in_cloud(rmcloud, rmapy_document_new)

    new_highlight = models.Highlight.create_highlight(
        rmapy_document_new.ID,
        "new_text",
        20,
        "manually added"
    )

    add_new_highlight(mock_extractor, new_highlight)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights([new_highlight], new_highlights)
    verify_documents([models.Document.from_cloud_document(rmapy_document_new)], new_documents)


def test_app_run_persist_returns_nothing_for_changed_document_with_no_new_highlights(
        rmcloud: rmcloud_.RMCloud,
        logger: log.CommandLineLogger,
        extractors: List[highlight_extractor.HighlightExtractor],
        sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
        documents: List[models.Document],
        highlights: List[models.Highlight],
        capsys: CaptureFixture,
        mock_extractor: highlight_extractor.HighlightExtractor,
        rmapy_document_new: document_.Document) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)
    # change updated at for document no new highlights

    new_highlight = models.Highlight.create_highlight(
        rmapy_document_new.ID,
        "new_text",
        20,
        "manually added"
    )

    add_new_document_and_store_in_cloud(rmcloud, rmapy_document_new)
    add_new_highlight(mock_extractor, new_highlight)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights([new_highlight], new_highlights)
    verify_documents([models.Document.from_cloud_document(rmapy_document_new)], new_documents)

    update_document_modified_at_and_store(rmcloud, models.Document.from_cloud_document(rmapy_document_new))

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Downloaded 1 document" in captured.err
    verify_highlights([], new_highlights)
    verify_documents([], new_documents)


def test_app_run_persist_returns_no_new_highlights_for_duplicate_highlights_in_same_document(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor,
    rmapy_document_new: document_.Document
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    new_highlight = models.Highlight.create_highlight(
        rmapy_document_new.ID,
        "new_text",
        20,
        "manually added"
    )
    # change update at for document with same highlight
    add_new_document_and_store_in_cloud(rmcloud, rmapy_document_new)
    add_new_highlight(mock_extractor, new_highlight)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "found 1 highlight" in captured.err
    assert "1 are new" in captured.err
    verify_highlights([new_highlight], new_highlights)
    verify_documents([models.Document.from_cloud_document(rmapy_document_new)], new_documents)

    same_new_highlight = models.Highlight.create_highlight(
        rmapy_document_new.ID,
        "new_text",
        21,
        "manually added"
    )
    add_new_highlight(mock_extractor, same_new_highlight)
    update_document_modified_at_and_store(rmcloud, models.Document.from_cloud_document(rmapy_document_new))

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "found 1 highlight" in captured.err
    assert "0 are new" in captured.err
    verify_highlights([], new_highlights)
    verify_documents([], new_documents)


def test_app_run_persist_returns_nothing_for_new_document_with_no_highlights(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor,
    rmapy_document_new: document_.Document
) -> None:

    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    add_new_document_and_store_in_cloud(rmcloud, rmapy_document_new)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Downloaded 1 document" in captured.err
    assert "found 0 highlight" in captured.err
    assert "0 are new" in captured.err
    verify_highlights([], new_highlights)
    verify_documents([], new_documents)


def test_app_run_updates_documents(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
) -> None:
    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    previous_documents = sqlalchemy_storage.get_documents([documents[0].id])
    assert len(previous_documents) == 1
    previous_document = previous_documents[0]

    update_document_modified_at_and_store(rmcloud, documents[0])

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    assert captured.out == ""
    assert captured.err != ""
    assert len(new_documents) == 0
    assert len(new_highlights) == 0

    modified_documents = sqlalchemy_storage.get_documents([documents[0].id])
    assert len(modified_documents) == 1
    modified_document = modified_documents[0]

    prev_doc_dict = previous_document.to_dict()
    modified_document_dict = modified_document.to_dict()
    assert prev_doc_dict != modified_document_dict

    prev_doc_dict.pop("modified_client")
    modified_document_dict.pop("modified_client")
    assert prev_doc_dict == modified_document_dict


def test_app_run_does_not_drop_duplicate_highlights_in_different_document(
    rmcloud: rmcloud_.RMCloud,
    logger: log.CommandLineLogger,
    extractors: List[highlight_extractor.HighlightExtractor],
    sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
    documents: List[models.Document],
    highlights: List[models.Highlight],
    capsys: CaptureFixture,
    mock_extractor: highlight_extractor.HighlightExtractor,
    rmapy_document_new: document_.Document
) -> None:

    app = app_.App(rmcloud=rmcloud, extractors=extractors, logger=logger, storage=sqlalchemy_storage)
    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    verify_highlights(highlights, new_highlights)
    verify_documents(documents, new_documents)

    new_highlight = models.Highlight.create_highlight(
        rmapy_document_new.ID,
        "new_text",
        20,
        "manually added"
    )
    # change update at for document with same highlight
    add_new_document_and_store_in_cloud(rmcloud, rmapy_document_new)
    add_new_highlight(mock_extractor, new_highlight)

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "found 1 highlight" in captured.err
    assert "1 are new" in captured.err
    verify_highlights([new_highlight], new_highlights)
    verify_documents([models.Document.from_cloud_document(rmapy_document_new)], new_documents)

    same_new_highlight = models.Highlight.create_highlight(
        documents[1].id,
        "new_text",
        20,
        "manually added"
    )
    add_new_highlight(mock_extractor, same_new_highlight)
    update_document_modified_at_and_store(rmcloud, models.Document.from_cloud_document(rmapy_document_new))
    update_document_modified_at_and_store(rmcloud, documents[1])

    new_documents, new_highlights = app.run_app("/tmp/434324", ["a_folder"])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "found 4 highlight" in captured.err
    assert "1 are new" in captured.err
    verify_highlights([same_new_highlight], new_highlights)
    verify_documents([documents[1]], new_documents)
