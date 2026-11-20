from domain.rag.entities import RAGResult
from domain.rag.repositories import Retriever
from domain.rag.llm import LLMProvider
from domain.rag.validators import validate_question, validate_top_k

from .prompt_builder import build_prompt


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
        validate_question(question)
        validate_top_k(top_k)

        chunks = self.retriever.retrieve(question, top_k)

        prompt = build_prompt(question, chunks)

        answer = self.llm.generate(prompt)

        return RAGResult(
            question=question,
            answer=answer,
            sources=tuple(chunks)
        )