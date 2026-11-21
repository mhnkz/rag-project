from django.urls import path

from .views import (
    DocumentListView,
    DocumentDetailView,
    DocumentUploadView,
    DocumentDeleteView,
)

urlpatterns = [
    path("", DocumentListView.as_view(), name="document-list"),
    path("upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("<int:pk>/delete/", DocumentDeleteView.as_view(), name="document-delete"),
]