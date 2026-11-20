from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    document_id: int
    chunk_index: int
    content: str

    def __post_init__(self):
        if self.document_id <= 0:
            raise ValueError("document_id must be positive")

        if self.chunk_index < 0:
            raise ValueError("chunk_index cannot be negative")

        if not self.content.strip():
            raise ValueError("chunk content cannot be empty")