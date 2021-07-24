# pylint: disable=no-self-use,missing-function-docstring


import typing as T

from rmapy import document as document_
from sqlalchemy import Column, Integer, String, orm

from remarking import models


class ModelMixInTest(models.Base, models.ModelMixIn):
    """ Test model for ModelMixIn """
    __tablename__ = "model_mix_in_test"
    string: str = Column(String(255), primary_key=True)
    number: int = Column(Integer)


class TestModelMixIn():

    def test_from_dict(self, db_session: orm.Session) -> None:
        model = ModelMixInTest.from_dict({
            "string": "model",
            "number": 10
        })
        assert model.string == "model"
        assert model.number == 10

    def test_to_dict(self, db_session: orm.Session) -> None:
        mixin = ModelMixInTest(
            string="model",
            number=10
        )
        mix_in_dict = mixin.to_dict()
        assert mix_in_dict == {
            "string": "model",
            "number": 10
        }

    def test_repr(self, db_session: orm.Session) -> None:
        mixin = ModelMixInTest(
            string="model",
            number=10
        )
        assert str(mixin) == "ModelMixInTest({'string': 'model', 'number': 10})"


class TestDocument():

    def test_from_cloud_document(self, rmapy_document: document_.Document,
                                 document_data: T.Dict[str, T.Any]) -> None:
        document_model = models.Document.from_cloud_document(rmapy_document)
        assert document_model.id == document_data['ID']
        assert document_model.version == document_data['Version']
        assert document_model.modified_client.isoformat() == document_data['ModifiedClient']
        assert document_model.type == document_data['Type']
        assert document_model.name == document_data['VissibleName']
        assert document_model.current_page == document_data['CurrentPage']
        assert document_model.bookmarked == document_data['Bookmarked']
        assert document_model.parent == document_data['Parent']

    def test_to_metadata_dict(self, rmapy_document: document_.Document,
                              document_data: T.Dict[str, T.Any]) -> None:
        document_model = models.Document.from_cloud_document(rmapy_document)
        data = document_model.to_metadata_dict()
        assert data['deleted'] is False
        assert data['lastModified'] == document_model.modified_client.timestamp()
        assert data['lastOpenedPage'] == document_data['CurrentPage']
        assert data['metadatamodified'] is False
        assert data['parent'] == document_data['Parent']
        assert data['pinned'] is False
        assert data['synced'] is True
        assert data['type'] == document_data['Type']
        assert data['version'] == document_data['Version']
        assert data['visibleName'] == document_data['VissibleName']

    def test_equal(self, rmapy_document: document_.Document, rmapy_document_2: document_.Document) -> None:
        document_model_1 = models.Document.from_cloud_document(rmapy_document)
        document_model_2 = models.Document.from_cloud_document(rmapy_document)
        document_model_3 = models.Document.from_cloud_document(rmapy_document_2)

        assert document_model_1.equal(document_model_1)
        assert document_model_1.equal(document_model_2)

        assert not document_model_1.equal(document_model_3)
        assert not document_model_2.equal(document_model_3)


class TestHighlights():

    def test_equal(self, highlight: models.Highlight) -> None:
        highlight2 = models.Highlight.create_highlight(
            highlight.document_id,
            "text_different",
            20,
            "Unextracted"
        )

        highlight3 = models.Highlight.create_highlight(
            "another_doc_id",
            "text_different",
            20,
            "Unextracted"
        )

        highlight_same = models.Highlight.create_highlight(
            highlight.document_id,
            highlight.text,
            10,
            "Unextracted"
        )

        highlight_same_different_page = models.Highlight.create_highlight(
            highlight.document_id,
            highlight.text,
            20,
            "Unextracted"
        )

        assert not highlight.equal(highlight_same_different_page)
        assert highlight.equal(highlight_same)
        assert highlight.equal(highlight)
        assert not highlight.equal(highlight2)
        assert not highlight.equal(highlight3)

    def test_create_highlight(self) -> None:
        highlight = models.Highlight.create_highlight(
            "123",
            "document",
            20,
            "Unextracted"
        )
        assert highlight.document_id == "123"
        assert highlight.text == "document"
        assert highlight.page_number == 20
        assert highlight.extraction_method == "Unextracted"
