from typing import Protocol

from .entities import RetrievedChunk


class Retriever(Protocol):
    def retrieve(
        self,
        query: str,
        top_k: int
    ) -> list[RetrievedChunk]:
        ...