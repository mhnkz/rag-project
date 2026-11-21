from functools import lru_cache

from django.conf import settings

from application.questions.use_cases import AskQuestionUseCase
from infrastructure.llm.openrouter_provider import OpenRouterLLMProvider
from infrastructure.vector_store.chroma_repository import ChromaRepository


@lru_cache(maxsize=1)
def get_ask_question_use_case() -> AskQuestionUseCase:
    retriever = ChromaRepository()

    llm = OpenRouterLLMProvider(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        model=settings.OPENROUTER_MODEL,
        connect_timeout=settings.OPENROUTER_CONNECT_TIMEOUT,
        read_timeout=settings.OPENROUTER_READ_TIMEOUT,
        max_retries=settings.OPENROUTER_MAX_RETRIES,
        retry_backoff=settings.OPENROUTER_RETRY_BACKOFF
    )

    return AskQuestionUseCase(
        retriever=retriever,
        llm=llm
    )


def ask_question(
    question: str,
    top_k: int = 5
):
    use_case = get_ask_question_use_case()

    return use_case.execute(
        question=question,
        top_k=top_k
    )