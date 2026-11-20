from django.contrib import admin
from .models import Question, Source


class SourceInline(admin.TabularInline):
    model = Source
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('answer', 'created_at')
    inlines = [SourceInline]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('question', 'document', 'chunk_index', 'score')
    list_filter = ('document',)
    search_fields = ('content', 'document__title')