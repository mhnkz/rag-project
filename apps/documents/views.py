import logging

from django.db import transaction
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError

from infrastructure.vector_store.chroma_repository import ChromaRepository

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services import ingest_document

logger = logging.getLogger(__name__)


class DocumentListView(ListAPIView):
    queryset = Document.objects.all().order_by("-created_at")
    serializer_class = DocumentSerializer


class DocumentDetailView(RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document = serializer.save()

        try:
            ingest_document(document.id)
        except Exception:
            logger.exception("Document ingestion failed: %s", document.id)

        document.refresh_from_db()

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )


class DocumentDeleteView(APIView):
    def delete(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            ChromaRepository().delete_chunks(document.id)
        except Exception:
            logger.exception("Failed to delete vector chunks.")
            return Response(
                {"detail": "Failed to delete document vectors."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        file = document.file

        with transaction.atomic():
            document.delete()

        if file:
            file.delete(save=False)

        return Response(status=status.HTTP_204_NO_CONTENT)