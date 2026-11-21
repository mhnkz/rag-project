from unittest.mock import Mock, call

import pytest

from application.documents.ingest_use_case import (
    IngestDocumentUseCase,
)
from domain.documents.entities import DocumentChunk


def create_use_case():
    loader = Mock(return_value="Document text")
    chunker = Mock(return_value=["Chunk 1", "Chunk 2"])
    repository = Mock()

    use_case = IngestDocumentUseCase(
        loader=loader,
        chunker=chunker,
        repository=repository
    )

    return use_case, loader, chunker, repository


def test_ingest_document_success():
    use_case, loader, chunker, repository = create_use_case()

    result = use_case.execute(
        document_id=1,
        document_title="Test Document",
        file_path="test.docx"
    )

    loader.assert_called_once_with("test.docx")
    chunker.assert_called_once_with("Document text")

    repository.delete_chunks.assert_called_once_with(1)
    repository.save_chunks.assert_called_once_with(result)

    assert result == [
        DocumentChunk(
            document_id=1,
            document_title="Test Document",
            chunk_index=0,
            content="Chunk 1"
        ),
        DocumentChunk(
            document_id=1,
            document_title="Test Document",
            chunk_index=1,
            content="Chunk 2"
        )
    ]


def test_ingest_deletes_old_chunks_before_saving():
    use_case, loader, chunker, repository = create_use_case()

    use_case.execute(
        document_id=1,
        document_title="Test Document",
        file_path="test.docx"
    )

    assert repository.method_calls == [
        call.delete_chunks(1),
        call.save_chunks(
            [
                DocumentChunk(
                    document_id=1,
                    document_title="Test Document",
                    chunk_index=0,
                    content="Chunk 1"
                ),
                DocumentChunk(
                    document_id=1,
                    document_title="Test Document",
                    chunk_index=1,
                    content="Chunk 2"
                )
            ]
        )
    ]


@pytest.mark.parametrize("text", ["", "   ", "\n"])
def test_ingest_rejects_empty_text(text):
    loader = Mock(return_value=text)
    chunker = Mock()
    repository = Mock()

    use_case = IngestDocumentUseCase(
        loader=loader,
        chunker=chunker,
        repository=repository
    )

    with pytest.raises(ValueError, match="Document contains no text"):
        use_case.execute(1, "Test Document", "test.docx")

    chunker.assert_not_called()
    repository.delete_chunks.assert_not_called()
    repository.save_chunks.assert_not_called()


def test_ingest_rejects_empty_chunks():
    loader = Mock(return_value="Document text")
    chunker = Mock(return_value=[])
    repository = Mock()

    use_case = IngestDocumentUseCase(
        loader=loader,
        chunker=chunker,
        repository=repository
    )

    with pytest.raises(ValueError, match="Document produced no chunks"):
        use_case.execute(1, "Test Document", "test.docx")

    repository.delete_chunks.assert_not_called()
    repository.save_chunks.assert_not_called()