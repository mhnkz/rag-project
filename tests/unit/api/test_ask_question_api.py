
import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.questions.models import Question, Source
from apps.documents.models import Document
from domain.rag.entities import RAGResult, RetrievedChunk
from application.questions.exceptions import QuestionServiceError


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
@patch("apps.questions.views.ask_question")
def test_ask_question_success(mock_ask, client):
    document = Document.objects.create(
        title="Guide",
        file="documents/guide.docx",
        status="completed"
    )

    chunk = RetrievedChunk(
        document_id=document.id,
        document_title="Guide",
        chunk_index=0,
        content="Water is essential for life.",
        score=0.25
    )

    mock_ask.return_value = RAGResult(
        question="What is water?",
        answer="Water is essential for life.",
        sources=(chunk,)
    )

    response = client.post(
        "/api/questions/ask/",
        {
            "question": "What is water?",
            "top_k": 3
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["answer"] == "Water is essential for life."
    assert len(response.data["sources"]) == 1

    assert Question.objects.count() == 1
    assert Source.objects.count() == 1

    saved_question = Question.objects.first()
    assert saved_question.question == "What is water?"
    assert saved_question.answer == "Water is essential for life."

    mock_ask.assert_called_once_with(
        question="What is water?",
        top_k=3
    )


@pytest.mark.django_db
@patch("apps.questions.views.ask_question")
def test_invalid_question(mock_ask, client):
    response = client.post(
        "/api/questions/ask/",
        {
            "question": "",
            "top_k": 3
        },
        format="json"
    )

    assert response.status_code == 400
    assert Question.objects.count() == 0
    assert Source.objects.count() == 0
    mock_ask.assert_not_called()


@patch("apps.questions.views.ask_question")
def test_question_service_error(mock_ask, client):
    mock_ask.side_effect = QuestionServiceError(
        "Provider failed"
    )

    response = client.post(
        "/api/questions/ask/",
        {
            "question": "What is water?",
            "top_k": 3
        },
        format="json"
    )

    assert response.status_code == 502
    assert response.data["error"] == (
        "Question answering service is temporarily unavailable."
    )


@patch("apps.questions.views.ask_question")
def test_unexpected_error(mock_ask, client):
    mock_ask.side_effect = RuntimeError("Unexpected failure")

    response = client.post(
        "/api/questions/ask/",
        {
            "question": "What is water?",
            "top_k": 3
        },
        format="json"
    )

    assert response.status_code == 500
    assert response.data["error"] == (
        "An internal server error occurred."
    )
