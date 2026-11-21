
from domain.rag.entities import RAGResult
from domain.rag.repositories import Retriever
from domain.rag.llm import LLMProvider
from domain.rag.validators import validate_question, validate_top_k

from .prompt_builder import build_prompt
from .exceptions import QuestionValidationError, QuestionServiceError


class AskQuestionUseCase:
    def __init__(
        self,
        retriever: Retriever,
        llm: LLMProvider
    ):
        self.retriever = retriever
        self.llm = llm

    def execute(
        self,
        question: str,
        top_k: int = 5
    ) -> RAGResult:
        try:
            validate_question(question)
            validate_top_k(top_k)
        except ValueError as error:
            raise QuestionValidationError(str(error)) from error

        try:
            chunks = self.retriever.retrieve(question, top_k)
            prompt = build_prompt(question, chunks)
            answer = self.llm.generate(prompt)

        except Exception as error:
            raise QuestionServiceError(
                "Question answering service failed"
            ) from error

        return RAGResult(
            question=question,
            answer=answer,
            sources=tuple(chunks)
        )
