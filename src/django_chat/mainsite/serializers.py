# fileupload/serializers.py
from rest_framework import serializers
from .models import UploadFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = ['file', 'uploaded_at']
