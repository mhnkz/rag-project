from django.contrib import admin, messages

from infrastructure.vector_store.chroma_repository import ChromaRepository

from .models import Document
from .services import ingest_document


@admin.action(description="Process selected documents")
def process_documents(modeladmin, request, queryset):
    processed = 0
    failed = 0

    for document in queryset:
        try:
            ingest_document(document.id)
            processed += 1

        except Exception as error:
            failed += 1

            modeladmin.message_user(
                request,
                f"{document.title}: {error}",
                level=messages.ERROR
            )

    if processed:
        modeladmin.message_user(
            request,
            f"{processed} document(s) processed successfully.",
            level=messages.SUCCESS
        )

    if failed:
        modeladmin.message_user(
            request,
            f"{failed} document(s) failed.",
            level=messages.WARNING
        )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = ("status",)

    search_fields = ("title",)

    readonly_fields = (
        "status",
        "extracted_text",
        "error_message",
        "created_at",
        "updated_at",
    )

    actions = [process_documents]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Process automatically on upload or when the file is replaced.
        if not change or "file" in form.changed_data:
            try:
                ingest_document(obj.pk)

                self.message_user(
                    request,
                    "Document processed successfully.",
                    level=messages.SUCCESS
                )

            except Exception as error:
                self.message_user(
                    request,
                    f"Processing failed: {error}",
                    level=messages.ERROR
                )

    def delete_model(self, request, obj):
        ChromaRepository().delete_chunks(obj.pk)

        file = obj.file

        super().delete_model(request, obj)

        if file:
            file.delete(save=False)

    def delete_queryset(self, request, queryset):
        repository = ChromaRepository()
        files = []

        for document in queryset:
            repository.delete_chunks(document.pk)
            files.append(document.file)

        super().delete_queryset(request, queryset)

        for file in files:
            if file:
                file.delete(save=False)