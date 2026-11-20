from langchain_chroma import Chroma

from domain.documents.entities import DocumentChunk
from domain.documents.repositories import DocumentChunkRepository
from domain.rag.entities import RetrievedChunk
from domain.rag.repositories import Retriever

from infrastructure.embeddings.embedding_service import (
    SentenceTransformerEmbeddingService
)


class ChromaRepository(DocumentChunkRepository, Retriever):
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "rag_documents",
        embedding_service=None
    ):
        if embedding_service is None:
            embedding_service = SentenceTransformerEmbeddingService()

        self.store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_service,
            persist_directory=persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )

    def save_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        ids = [
            f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}"
            for chunk in chunks
        ]

        texts = [chunk.content for chunk in chunks]

        metadatas = [
            {
                "document_id": chunk.document_id,
                "document_title": chunk.document_title,
                "chunk_index": chunk.chunk_index
            }
            for chunk in chunks
        ]

        self.store.upsert(
            ids=ids,
            texts=texts,
            metadatas=metadatas
        )

    def delete_chunks(self, document_id: int) -> None:
        self.store.delete(
            ids=self.store.get(
                where={"document_id": document_id}
            )["ids"]
        )

    def retrieve(
        self,
        query: str,
        top_k: int
    ) -> list[RetrievedChunk]:
        results = self.store.similarity_search_with_score(
            query,
            k=top_k
        )

        chunks = []

        for document, score in results:
            metadata = document.metadata

            chunks.append(
                RetrievedChunk(
                    document_id=metadata["document_id"],
                    document_title=metadata["document_title"],
                    chunk_index=metadata["chunk_index"],
                    content=document.page_content,
                    score=float(score)
                )
            )

        return chunks