from django.db import models


class Question(models.Model):
    question = models.TextField()

    answer = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:100]


class Source(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='sources'
    )

    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='sources'
    )

    chunk_index = models.PositiveIntegerField()

    content = models.TextField()

    score = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'document', 'chunk_index'],
                name='unique_question_document_chunk'
            )
        ]

    def __str__(self):
        return f'{self.document.title} - Chunk {self.chunk_index}'