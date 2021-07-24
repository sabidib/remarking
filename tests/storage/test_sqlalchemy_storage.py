# pylint: disable=no-self-use,missing-function-docstring

import pytest
from pytest_unordered import unordered
from rmapy import document as document_

from remarking import models
from remarking.storage import sqlalchemy_storage as sqlalchemy_storage_


@pytest.fixture()
def document(rmapy_document: document_.Document) -> models.Document:
    document_model = models.Document.from_cloud_document(rmapy_document)
    return document_model


@pytest.fixture()
def document_2(rmapy_document_2: document_.Document) -> models.Document:
    document_model = models.Document.from_cloud_document(rmapy_document_2)
    return document_model


def test_sqlalchemy_storage(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage) -> None:
    assert not sqlalchemy_storage.echo


def test_save_models_single(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                            highlight: models.Highlight, document: models.Document) -> None:
    sqlalchemy_storage.save_models([highlight])
    highlights = sqlalchemy_storage.get_highlights()
    assert len(highlights) == 1
    assert highlights[0].equal(highlight)


def test_save_models_multiple(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                              highlight: models.Highlight, document: models.Document) -> None:
    sqlalchemy_storage.save_models([highlight, document])
    highlights = sqlalchemy_storage.get_highlights()
    documents = sqlalchemy_storage.get_documents()
    assert len(highlights) == 1
    assert highlights[0].equal(highlight)

    documents = sqlalchemy_storage.get_documents()
    assert len(documents) == 1
    assert documents[0].equal(document)


def test_update_documents(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                          document: models.Document, document_2: models.Document) -> None:
    sqlalchemy_storage.save_models([document, document_2])
    assert unordered([doc.id for doc in sqlalchemy_storage.get_documents()]) == [document_2.id, document.id]

    document.name = "anothername"
    sqlalchemy_storage.update_documents([document])
    documents = sqlalchemy_storage.get_documents([document.id])
    assert len(documents) == 1
    assert documents[0].name == "anothername"

    sqlalchemy_storage.commit()

    document.name = "anothername1"
    document_2.name = "anothername2"
    sqlalchemy_storage.update_documents([document, document_2])
    documents = sqlalchemy_storage.get_documents()
    assert len(documents) == 2
    assert unordered(doc.name for doc in documents) == ["anothername1", "anothername2"]


def test_get_documents(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                       highlight: models.Highlight, document: models.Document, document_2: models.Document) -> None:
    sqlalchemy_storage.save_models([highlight, document, document_2])
    assert unordered([doc.id for doc in sqlalchemy_storage.get_documents()]) == [document_2.id, document.id]

    documents = sqlalchemy_storage.get_documents([document.id])
    assert len(documents) == 1
    assert documents[0].equal(document)

    documents = sqlalchemy_storage.get_documents([document_2.id])
    assert len(documents) == 1
    assert documents[0].equal(document_2)

    documents = sqlalchemy_storage.get_documents([document.id, document_2.id])
    assert len(documents) == 2
    assert unordered([doc.id for doc in documents]) == [document_2.id, document.id]


def test_get_highlights(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                        highlight: models.Highlight, highlight_2: models.Highlight) -> None:
    sqlalchemy_storage.save_models([highlight, highlight_2])

    highlights = sqlalchemy_storage.get_highlights()
    assert len(highlights) == 2
    assert unordered(highlight_.hash for highlight_ in highlights) == [highlight.hash, highlight_2.hash]

    highlights = sqlalchemy_storage.get_highlights([highlight.hash])
    assert len(highlights) == 1
    assert highlights[0].equal(highlight)

    highlights = sqlalchemy_storage.get_highlights([highlight_2.hash])
    assert len(highlights) == 1
    assert highlights[0].equal(highlight_2)

    highlights = sqlalchemy_storage.get_highlights([highlight.hash, highlight_2.hash])
    assert len(highlights) == 2
    assert unordered(highlight_.hash for highlight_ in highlights) == [highlight.hash, highlight_2.hash]


def test_commit(sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
                document: models.Document, document_2: models.Document) -> None:
    sqlalchemy_storage.save_models([document, document_2])
    assert unordered([doc.id for doc in sqlalchemy_storage.get_documents()]) == [document_2.id, document.id]

    document.name = "anothername"
    sqlalchemy_storage.update_documents([document])
    documents = sqlalchemy_storage.get_documents([document.id])
    assert len(documents) == 1
    assert documents[0].name == "anothername"

    document.name = "anothername1"
    sqlalchemy_storage.update_documents([document])
    documents = sqlalchemy_storage.get_documents([document.id])
    assert len(documents) == 1
    assert documents[0].name == "anothername1"
