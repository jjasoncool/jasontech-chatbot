# fileupload/urls.py
from django.urls import path
from .views import FileUploadView, test_chromadb_connection

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('test-chromadb/', test_chromadb_connection, name='test_chromadb_connection')
]
