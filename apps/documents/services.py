from application.documents.ingest_use_case import (
    IngestDocumentUseCase,
)

from infrastructure.document_loaders.docx_loader import load_docx
from infrastructure.text_processing.chunker import split_text
from infrastructure.vector_store.chroma_repository import ChromaRepository

from .models import Document


def ingest_document(document_id: int) -> None:
    document = Document.objects.get(pk=document_id)

    document.status = Document.Status.PROCESSING
    document.error_message = ""
    document.save(update_fields=["status", "error_message", "updated_at"])

    try:
        text = load_docx(document.file.path)

        use_case = IngestDocumentUseCase(
            loader=lambda _: text,
            chunker=split_text,
            repository=ChromaRepository()
        )

        chunks = use_case.execute(
            document_id=document.id,
            document_title=document.title,
            file_path=document.file.path
        )

        document.extracted_text = text
        document.status = Document.Status.COMPLETED
        document.error_message = ""

        document.save(
            update_fields=[
                "extracted_text",
                "status",
                "error_message",
                "updated_at"
            ]
        )

    except Exception as error:
        document.status = Document.Status.FAILED
        document.error_message = str(error)

        document.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at"
            ]
        )

        raise