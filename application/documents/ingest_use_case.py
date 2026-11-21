from domain.documents.entities import DocumentChunk
from domain.documents.repositories import DocumentChunkRepository


class IngestDocumentUseCase:
    def __init__(
        self,
        loader,
        chunker,
        repository: DocumentChunkRepository
    ):
        self.loader = loader
        self.chunker = chunker
        self.repository = repository

    def execute(
        self,
        document_id: int,
        document_title: str,
        file_path: str
    ) -> list[DocumentChunk]:

        text = self.loader(file_path)

        if not text or not text.strip():
            raise ValueError("Document contains no text")

        chunk_contents = self.chunker(text)

        if not chunk_contents:
            raise ValueError("Document produced no chunks")

        chunks = [
            DocumentChunk(
                document_id=document_id,
                document_title=document_title,
                chunk_index=index,
                content=content
            )
            for index, content in enumerate(chunk_contents)
        ]

        self.repository.delete_chunks(document_id)
        self.repository.save_chunks(chunks)

        return chunks