# fileupload/urls.py
from django.urls import path
from .views import FileUploadView, test_chromadb_connection, query_chromadb, visualize_chromadb, query_ollama

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('test-chromadb/', test_chromadb_connection, name='test_chromadb_connection'),
    path('query-chromadb/', query_chromadb, name='query_chromadb'),
    path('visualize-chromadb/', visualize_chromadb, name='visualize_chromadb'),
    path('query-ollama/', query_ollama, name='query_ollama'),
]
