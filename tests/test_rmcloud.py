# pylint: disable=no-self-use,missing-function-docstring,protected-access
import pytest
import rmapy
from rmapy import collections as collections_
from rmapy import document as document_
from rmapy import folder as folder_

from remarking import rmcloud as rmcloud_


@pytest.fixture
def rmcloud(mock_rmcloud: rmcloud_.RMCloud) -> rmcloud_.RMCloud:
    return mock_rmcloud


def test_rm_cloud_auth(rmcloud: rmcloud_.RMCloud) -> None:
    rmcloud._api_client.is_auth.return_value = False
    rmcloud._api_client.register_device.side_effect = rmapy.exceptions.AuthError("auth_error")
    with pytest.raises(rmcloud_.AuthError):
        rmcloud_.RMCloud("failtoken")

    rmcloud._api_client.register_device.side_effect = None
    with pytest.raises(rmcloud_.AuthError):
        rmcloud_.RMCloud("failtoken")

    rmcloud._api_client.is_auth.return_value = True
    rmcloud_.RMCloud("failtoken")


def test_get_meta_items(rmcloud: rmcloud_.RMCloud, rmapy_collection: collections_.Collection) -> None:
    items = rmcloud.get_meta_items()
    assert list(items) == list(rmapy_collection)


def test_get_folders(rmcloud: rmcloud_.RMCloud,
                     rmapy_folder: folder_.Folder,
                     rmapy_folder_2: folder_.Folder) -> None:
    folders = rmcloud.get_folders()
    assert sorted(folders, key=lambda x: x.ID) == sorted([rmapy_folder, rmapy_folder_2], key=lambda x: x.ID)

    folders = rmcloud.get_folders([rmapy_folder.VissibleName])
    assert folders == [rmapy_folder]

    folders = rmcloud.get_folders([rmapy_folder.VissibleName, rmapy_folder_2.VissibleName])
    assert folders == [rmapy_folder, rmapy_folder_2]

    folders = rmcloud.get_folders(["doesn't exist"])
    assert folders == []


def test_get_documents(rmcloud: rmcloud_.RMCloud, rmapy_document: document_.Document,
                       rmapy_document_2: document_.Document, rmapy_document_3: document_.Document) -> None:
    documents = rmcloud.get_documents()
    assert sorted(documents, key=lambda x: x.ID) == sorted([rmapy_document,
                                                            rmapy_document_2,
                                                            rmapy_document_3],
                                                           key=lambda x: x.ID)

    documents = rmcloud.get_documents([rmapy_document.VissibleName])
    assert documents == [rmapy_document]

    documents = rmcloud.get_documents([rmapy_document.VissibleName, rmapy_document_2.VissibleName])
    assert documents == [rmapy_document, rmapy_document_2]

    assert rmcloud.get_documents(["nothere"]) == []


def test_crawl_folders(rmcloud: rmcloud_.RMCloud,
                       rmapy_document: document_.Document,
                       rmapy_document_2: document_.Document,
                       rmapy_document_3: document_.Document,
                       rmapy_folder: folder_.Folder,
                       rmapy_folder_2: folder_.Folder) -> None:
    documents = rmcloud.crawl_folders([rmapy_folder])
    assert sorted(documents, key=lambda x: x.ID) == sorted(
        [rmapy_document, rmapy_document_2, rmapy_document_3], key=lambda x: x.ID)
    documents = rmcloud.crawl_folders([rmapy_folder_2])
    assert documents == [rmapy_document_2, rmapy_document_3]


@pytest.mark.skip()
def test_download_document() -> None:
    pass
