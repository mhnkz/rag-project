from typing import Protocol

from .entities import DocumentChunk


class DocumentChunkRepository(Protocol):
    def save_chunks(self, chunks: list[DocumentChunk]) -> None:
        ...

    def delete_chunks(self, document_id: int) -> None:
        ...