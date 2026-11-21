from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "file"]

    def validate_file(self, value):
        if not value.name.lower().endswith(".docx"):
            raise serializers.ValidationError(
                "Only DOCX files are supported."
            )

        return value