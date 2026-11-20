import pytest

from domain.documents.entities import DocumentChunk
from domain.rag.entities import RetrievedChunk, RAGResult


def test_valid_document_chunk():
    chunk = DocumentChunk(
        document_id=1,
        chunk_index=0,
        content="Some text"
    )

    assert chunk.document_id == 1
    assert chunk.chunk_index == 0


@pytest.mark.parametrize("document_id", [0, -1])
def test_invalid_document_id(document_id):
    with pytest.raises(ValueError):
        DocumentChunk(document_id, 0, "Some text")


@pytest.mark.parametrize("chunk_index", [-1])
def test_invalid_chunk_index(chunk_index):
    with pytest.raises(ValueError):
        DocumentChunk(1, chunk_index, "Some text")


def test_empty_chunk_content():
    with pytest.raises(ValueError):
        DocumentChunk(1, 0, "   ")


def test_rag_result():
    source = RetrievedChunk(
        document_id=1,
        document_title="Guide",
        chunk_index=0,
        content="Some text",
        score=0.8
    )

    result = RAGResult(
        question="What is RAG?",
        answer="RAG combines retrieval and generation.",
        sources=(source,)
    )

    assert result.sources[0].document_id == 1
    assert result.answer != ""