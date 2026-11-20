from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    score: float | None = None


@dataclass(frozen=True)
class RAGResult:
    question: str
    answer: str
    sources: tuple[RetrievedChunk, ...]