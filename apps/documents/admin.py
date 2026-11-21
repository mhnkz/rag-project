from django.contrib import admin, messages

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