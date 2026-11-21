
import logging

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from .models import Question, Source
from .services import ask_question

from application.questions.exceptions import (
    QuestionValidationError,
    QuestionServiceError
)

logger = logging.getLogger(__name__)


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )

    top_k = serializers.IntegerField(
        required=False,
        default=5,
        min_value=1
    )


class AskQuestionView(APIView):
    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        question_text = serializer.validated_data["question"]
        top_k = serializer.validated_data["top_k"]

        try:
            result = ask_question(
                question=question_text,
                top_k=top_k
            )

        except QuestionValidationError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except QuestionServiceError:
            logger.exception("Question service failed")

            return Response(
                {
                    "error": (
                        "Question answering service is "
                        "temporarily unavailable."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception:
            logger.exception("Unexpected error in ask question API")

            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        with transaction.atomic():
            question = Question.objects.create(
                question=result.question,
                answer=result.answer
            )

            sources = [
                Source(
                    question=question,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=chunk.score
                )
                for chunk in result.sources
            ]

            Source.objects.bulk_create(sources)

        return Response(
            {
                "id": question.id,
                "question": question.question,
                "answer": question.answer,
                "sources": [
                    {
                        "document_id": chunk.document_id,
                        "document_title": chunk.document_title,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "score": chunk.score
                    }
                    for chunk in result.sources
                ],
                "created_at": question.created_at
            },
            status=status.HTTP_200_OK
        )
