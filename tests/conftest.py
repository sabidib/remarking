# pylint: disable=no-self-use,missing-function-docstring,protected-access
import typing as T
from typing import Dict, Iterator, List
from unittest.mock import MagicMock, create_autospec

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from rmapy import collections as collections_
from rmapy import document as document_
from rmapy import folder as folder_
from sqlalchemy import create_engine, orm

from remarking import models
from remarking import rmcloud as rmcloud_
from remarking.cli import app as app_
from remarking.cli import cli, common, extract, log
from remarking.storage import sqlalchemy_storage as sqlalchemy_storage_


@pytest.fixture(params=[
    ["run", "json"],
    ["persist", "--sqlalchemy", "sqlite///:memory:", "json"]
])
def cmd_start(request: T.Any) -> List[str]:
    return request.param


@pytest.fixture(scope="function", autouse=True)
def is_requests(monkeypatch: MonkeyPatch) -> None:
    def is_requesting(*args: T.Any, **kwargs: T.Any) -> None:
        raise Exception("Found requests leaving tests! Breakpoint here and check tracepoint to see what.")
    monkeypatch.setattr(requests, "request", is_requesting)


@pytest.fixture()
def rmapy_folder() -> folder_.Folder:
    return folder_.Folder(**{
        "ID": "123123",
        "Version": "1",
        "Message": "",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "",
        "VissibleName": "a_folder",
        "Parent": ""
    })


@pytest.fixture()
def rmapy_folder_2(rmapy_folder: folder_.Folder) -> folder_.Folder:
    return folder_.Folder(**{
        "ID": "432432",
        "Version": "1",
        "Message": "",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "",
        "VissibleName": "a_folder_2",
        "Parent": rmapy_folder.ID
    })


@pytest.fixture
def document_data(rmapy_folder: folder_.Folder) -> Dict[str, T.Any]:
    return {
        "ID": "1111",
        "Version": "2",
        "Message": "2",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "DocumentType",
        "VissibleName": "a_book",
        "CurrentPage": 10,
        "Bookmarked": False,
        "Parent": rmapy_folder.ID
    }


@pytest.fixture
def document_data_2(rmapy_folder_2: folder_.Folder) -> Dict[str, T.Any]:
    return {
        "ID": "22222",
        "Version": "2",
        "Message": "2",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "DocumentType",
        "VissibleName": "a_book_2",
        "CurrentPage": 10,
        "Bookmarked": False,
        "Parent": rmapy_folder_2.ID
    }


@pytest.fixture
def document_data_3(rmapy_folder_2: folder_.Folder) -> Dict[str, T.Any]:
    return {
        "ID": "33333",
        "Version": "2",
        "Message": "2",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "DocumentType",
        "VissibleName": "a_book_3",
        "CurrentPage": 10,
        "Bookmarked": False,
        "Parent": rmapy_folder_2.ID
    }


@pytest.fixture
def document_data_new(rmapy_folder: folder_.Folder) -> Dict[str, T.Any]:
    return {
        "ID": "99999",
        "Version": "2",
        "Message": "2",
        "Success": True,
        "BlobURLGet": "",
        "BlobURLGetExpires": "",
        "BlobURLPut": "",
        "BlobURLPutExpires": "",
        "ModifiedClient": "2020-01-01T20:00:00",
        "Type": "DocumentType",
        "VissibleName": "a_book_new",
        "CurrentPage": 20,
        "Bookmarked": False,
        "Parent": rmapy_folder.ID
    }


@pytest.fixture()
def rmapy_document(document_data: Dict[str, T.Any]) -> document_.Document:
    return document_.Document(**document_data)


@pytest.fixture()
def rmapy_document_2(document_data_2: Dict[str, T.Any]) -> document_.Document:
    return document_.Document(**document_data_2)


@pytest.fixture()
def rmapy_document_3(document_data_3: Dict[str, T.Any]) -> document_.Document:
    return document_.Document(**document_data_3)


@pytest.fixture()
def rmapy_document_new(document_data_new: Dict[str, T.Any]) -> document_.Document:
    return document_.Document(**document_data_new)


@pytest.fixture()
def rmapy_collection(rmapy_folder: document_.Document,
                     rmapy_folder_2: document_.Document,
                     rmapy_document: document_.Document,
                     rmapy_document_2: document_.Document,
                     rmapy_document_3: document_.Document) -> collections_.Collection:
    collection_data = [
        rmapy_folder,
        rmapy_folder_2,
        rmapy_document,
        rmapy_document_2,
        rmapy_document_3,
    ]
    return collections_.Collection(*collection_data)


@pytest.fixture()
def db_session() -> Iterator[orm.Session]:
    engine = create_engine('sqlite:///:memory:')
    sessionmaker = orm.sessionmaker(bind=engine)
    models.Base.metadata.create_all(engine)
    session = sessionmaker()
    yield session
    models.Base.metadata.drop_all(engine)


@pytest.fixture
def documents(rmapy_document: document_.Document,
              rmapy_document_2: document_.Document,
              rmapy_document_3: document_.Document) -> List[models.Document]:
    return [
        models.Document.from_cloud_document(rmapy_document),
        models.Document.from_cloud_document(rmapy_document_2),
        models.Document.from_cloud_document(rmapy_document_3),
    ]


@pytest.fixture()
def highlight_1(documents: List[models.Document]) -> models.Highlight:
    return models.Highlight.create_highlight(
        documents[0].id,
        "text_1",
        10,
        "Unextracted"
    )


@pytest.fixture()
def highlight(highlight_1: models.Highlight) -> models.Highlight:
    return highlight_1


@pytest.fixture()
def highlight_2(documents: List[models.Document]) -> models.Highlight:
    return models.Highlight.create_highlight(
        documents[1].id,
        "long_highlight " * 100,
        0,
        "Unextracted"
    )


@pytest.fixture()
def highlight_3(documents: List[models.Document]) -> models.Highlight:
    return models.Highlight.create_highlight(
        documents[1].id,
        "short_highlight",
        2,
        "Unextracted"
    )


@pytest.fixture()
def highlight_3_duplicate(documents: List[models.Document]) -> models.Highlight:
    return models.Highlight.create_highlight(
        documents[1].id,
        "short_highlight",
        2,
        "Different from 3, but same hash"
    )


@pytest.fixture()
def highlight_4_no_corresponding_document() -> models.Highlight:
    return models.Highlight.create_highlight(
        "id-that-doesnt-exist",
        "short_highlight",
        15,
        "Unextracted"
    )


@pytest.fixture
def highlights(highlight_1: models.Highlight,
               highlight_2: models.Highlight,
               highlight_3: models.Highlight,
               highlight_3_duplicate: models.Highlight) -> List[models.Highlight]:
    return [
        highlight_1,
        highlight_2,
        highlight_3,
        highlight_3_duplicate,
    ]


@pytest.fixture()
def isatty(monkeypatch: MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(log.click._compat, "isatty", lambda x: True)
    monkeypatch.setattr(log, "isatty", lambda: True)
    yield


@pytest.fixture()
def isnotatty(monkeypatch: MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(log.click._compat, "isatty", lambda x: False)
    monkeypatch.setattr(log, "isatty", lambda: False)
    yield


@pytest.fixture
def logger() -> log.CommandLineLogger:
    return log.CommandLineLogger()


@pytest.fixture
def mock_rmcloud(monkeypatch: MonkeyPatch, rmapy_collection: collections_.Collection) -> Iterator[rmcloud_.RMCloud]:
    client_object = create_autospec(spec=rmcloud_.rmapi.Client)
    client_return = MagicMock(return_value=client_object)
    client_object.get_meta_items.return_value = rmapy_collection
    client_object.is_auth.return_value = True
    monkeypatch.setattr(rmcloud_.rmapi, "Client", client_return)
    yield rmcloud_.RMCloud("token")


@pytest.fixture
def mock_sqlalchemy_storage(monkeypatch: MonkeyPatch,
                            highlights: T.List[models.Highlight],
                            documents: T.List[models.Document]) -> sqlalchemy_storage_.SqlAlchemyStorage:
    mock_sqlalchemy_storage_inst = MagicMock(autospec=cli.sqlalchemy_storage.SqlAlchemyStorage)
    mock_sqlalchemy_storage_class = MagicMock(return_value=mock_sqlalchemy_storage_inst)
    monkeypatch.setattr(cli.sqlalchemy_storage, "SqlAlchemyStorage", mock_sqlalchemy_storage_class)
    return mock_sqlalchemy_storage_inst


@pytest.fixture
def mock_app(monkeypatch: MonkeyPatch,
             highlights: T.List[models.Highlight],
             documents: T.List[models.Document],
             mock_sqlalchemy_storage: sqlalchemy_storage_.SqlAlchemyStorage,
             mock_rmcloud: rmcloud_.RMCloud) -> Iterator[app_.App]:
    mock_app_inst = MagicMock(autospec=app_.App)
    mock_app_class = MagicMock(return_value=mock_app_inst)
    mock_app_inst.run_app.return_value = (documents, highlights)
    monkeypatch.setattr(extract.app_, "App", mock_app_class)
    return mock_app_inst


@pytest.fixture()
def sqlalchemy_storage() -> sqlalchemy_storage_.SqlAlchemyStorage:
    storage = sqlalchemy_storage_.SqlAlchemyStorage("sqlite:///:memory:")
    yield storage
    models.Base.metadata.drop_all(storage._engine)


@pytest.fixture
def normalized_highlights(documents: T.List[models.Document],
                          highlights: T.List[models.Highlight]) -> T.List[Dict[str, T.Any]]:
    normalized = common.normalize_highlights_and_documents(documents, highlights)
    assert len(normalized) > 0
    return normalized
