from unittest.mock import Mock

from domain.documents.entities import DocumentChunk
from domain.rag.entities import RetrievedChunk

from infrastructure.vector_store.chroma_repository import ChromaRepository


def create_repository():
    embedding_service = Mock()

    repository = ChromaRepository(
        persist_directory="unused",
        embedding_service=embedding_service
    )

    repository.store = Mock()

    return repository


def test_save_chunks():
    repository = create_repository()

    chunks = [
        DocumentChunk(
            document_id=1,
            chunk_index=0,
            content="First chunk",
            document_title="RAG Guide"
        ),
        DocumentChunk(
            document_id=1,
            chunk_index=1,
            content="Second chunk",
            document_title="RAG Guide"
        )
    ]

    repository.save_chunks(chunks)

    repository.store.upsert.assert_called_once_with(
        ids=[
            "doc_1_chunk_0",
            "doc_1_chunk_1"
        ],
        texts=[
            "First chunk",
            "Second chunk"
        ],
        metadatas=[
            {
                "document_id": 1,
                "document_title": "RAG Guide",
                "chunk_index": 0
            },
            {
                "document_id": 1,
                "document_title": "RAG Guide",
                "chunk_index": 1
            }
        ]
    )


def test_save_empty_chunks():
    repository = create_repository()

    repository.save_chunks([])

    repository.store.upsert.assert_not_called()


def test_delete_chunks():
    repository = create_repository()

    repository.store.get.return_value = {
        "ids": [
            "doc_1_chunk_0",
            "doc_1_chunk_1"
        ]
    }

    repository.delete_chunks(1)

    repository.store.get.assert_called_once_with(
        where={"document_id": 1}
    )

    repository.store.delete.assert_called_once_with(
        ids=[
            "doc_1_chunk_0",
            "doc_1_chunk_1"
        ]
    )


def test_delete_chunks_when_document_has_no_chunks():
    repository = create_repository()

    repository.store.get.return_value = {"ids": []}

    repository.delete_chunks(1)

    repository.store.delete.assert_called_once_with(ids=[])


def test_retrieve():
    repository = create_repository()

    document = Mock()
    document.page_content = "RAG combines retrieval and generation."
    document.metadata = {
        "document_id": 1,
        "document_title": "RAG Guide",
        "chunk_index": 0
    }

    repository.store.similarity_search_with_score.return_value = [
        (document, 0.15)
    ]

    result = repository.retrieve(
        query="What is RAG?",
        top_k=3
    )

    repository.store.similarity_search_with_score.assert_called_once_with(
        "What is RAG?",
        k=3
    )

    assert result == [
        RetrievedChunk(
            document_id=1,
            document_title="RAG Guide",
            chunk_index=0,
            content="RAG combines retrieval and generation.",
            score=0.15
        )
    ]