from unittest.mock import Mock

import numpy as np

from infrastructure.embeddings.embedding_service import (
    SentenceTransformerEmbeddingService
)


def test_embed_documents(monkeypatch):
    model = Mock()
    model.encode.return_value = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ])

    monkeypatch.setattr(
        "infrastructure.embeddings.embedding_service.SentenceTransformer",
        lambda model_name: model
    )

    service = SentenceTransformerEmbeddingService()

    result = service.embed_documents([
        "Hello",
        "World"
    ])

    model.encode.assert_called_once_with(
        ["Hello", "World"],
        normalize_embeddings=True
    )

    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]


def test_embed_query(monkeypatch):
    model = Mock()
    model.encode.return_value = np.array([0.1, 0.2, 0.3])

    monkeypatch.setattr(
        "infrastructure.embeddings.embedding_service.SentenceTransformer",
        lambda model_name: model
    )

    service = SentenceTransformerEmbeddingService()

    result = service.embed_query("What is RAG?")

    model.encode.assert_called_once_with(
        "What is RAG?",
        normalize_embeddings=True
    )

    assert result == [0.1, 0.2, 0.3]