import logging

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from application.questions.exceptions import (
    QuestionServiceError,
    QuestionValidationError,
)

from .models import Question, Source
from .services import ask_question

logger = logging.getLogger(__name__)


class AskQuestionForm(forms.ModelForm):
    """
    Add form of the Question admin.

    The user types a question, and while the form is being validated
    we call the RAG pipeline. If it fails, the error is shown on the
    form and nothing is saved.
    """

    top_k = forms.IntegerField(
        label="Number of chunks (top_k)",
        min_value=1,
        max_value=20,
        initial=5,
        required=False,
        help_text="How many document chunks are retrieved as context.",
    )

    class Meta:
        model = Question
        fields = ["question"]
        widgets = {
            "question": forms.Textarea(attrs={"rows": 4, "cols": 80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag_result = None

    def clean(self):
        cleaned_data = super().clean()

        question = cleaned_data.get("question")

        if not question or self.errors:
            return cleaned_data

        top_k = cleaned_data.get("top_k") or 5

        try:
            self.rag_result = ask_question(
                question=question,
                top_k=top_k,
            )

        except (QuestionValidationError, ValueError) as error:
            raise forms.ValidationError(str(error))

        except QuestionServiceError:
            logger.exception("Question service failed")
            raise forms.ValidationError(
                "Question answering service is temporarily unavailable. "
                "Please try again."
            )

        except Exception:
            logger.exception("Unexpected error while asking question")
            raise forms.ValidationError(
                "An unexpected error occurred. Check the server logs."
            )

        return cleaned_data


class SourceInline(admin.TabularInline):
    """Read-only list of the chunks that were used for an answer."""

    model = Source
    extra = 0
    can_delete = False

    fields = ("document", "chunk_index", "score", "content")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = AskQuestionForm

    list_display = ("short_question", "short_answer", "created_at")
    search_fields = ("question", "answer")
    ordering = ("-created_at",)

    @admin.display(description="Question")
    def short_question(self, obj):
        return obj.question[:80]

    @admin.display(description="Answer")
    def short_answer(self, obj):
        return obj.answer[:80]

    def get_fields(self, request, obj=None):
        if obj is None:
            return ["question", "top_k"]

        return ["question", "answer", "created_at"]

    def get_inline_instances(self, request, obj=None):
        # No sources on the "add" page, only on saved questions.
        if obj is None:
            return []

        return [SourceInline(self.model, self.admin_site)]

    def has_change_permission(self, request, obj=None):
        # A saved question is history: it can be viewed or deleted,
        # but never edited.
        if obj is not None:
            return False

        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        result = form.rag_result

        obj.question = result.question
        obj.answer = result.answer

        super().save_model(request, obj, form, change)

        Source.objects.bulk_create([
            Source(
                question=obj,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=chunk.score,
            )
            for chunk in result.sources
        ])

    def response_add(self, request, obj, post_url_continue=None):
        # After asking, show the saved question with its answer
        # and sources instead of going back to the list.
        self.message_user(
            request,
            "Answer generated.",
            messages.SUCCESS,
        )

        return HttpResponseRedirect(
            reverse("admin:questions_question_change", args=[obj.pk])
        )


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("question", "document", "chunk_index", "score")
    list_filter = ("document",)
    search_fields = ("content", "document__title")