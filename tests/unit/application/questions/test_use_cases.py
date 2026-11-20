from unittest.mock import Mock

import pytest

from application.questions.use_cases import AskQuestionUseCase
from domain.rag.entities import RetrievedChunk


def test_ask_question_success():
    retriever = Mock()
    llm = Mock()

    chunks = [
        RetrievedChunk(
            document_id=1,
            document_title="RAG Guide",
            chunk_index=0,
            content="RAG combines retrieval and generation.",
            score=0.8
        )
    ]

    retriever.retrieve.return_value = chunks
    llm.generate.return_value = "RAG combines retrieval and generation."

    use_case = AskQuestionUseCase(retriever, llm)

    result = use_case.execute("What is RAG?", top_k=3)

    retriever.retrieve.assert_called_once_with("What is RAG?", 3)
    llm.generate.assert_called_once()

    assert result.question == "What is RAG?"
    assert result.answer == "RAG combines retrieval and generation."
    assert result.sources == tuple(chunks)


def test_invalid_question_does_not_call_dependencies():
    retriever = Mock()
    llm = Mock()

    use_case = AskQuestionUseCase(retriever, llm)

    with pytest.raises(ValueError):
        use_case.execute("   ")

    retriever.retrieve.assert_not_called()
    llm.generate.assert_not_called()


def test_invalid_top_k_does_not_call_dependencies():
    retriever = Mock()
    llm = Mock()

    use_case = AskQuestionUseCase(retriever, llm)

    with pytest.raises(ValueError):
        use_case.execute("What is RAG?", top_k=0)

    retriever.retrieve.assert_not_called()
    llm.generate.assert_not_called()