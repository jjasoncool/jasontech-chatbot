from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadFile
from .serializers import UploadedFileSerializer

from django.http import JsonResponse
from .chroma_client import ChromaDBClient

class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, *args, **kwargs):
        file_serializer = UploadedFileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test_chromadb_connection(request):
    # 初始化 ChromaDB 客戶端
    client = ChromaDBClient()

    # 測試插入和查詢
    try:
        test_vector = [0.1, 0.2, 0.3]  # 示例向量
        metadata = {"content": "This is a test content"}  # 測試元數據
        client.insert_vector(test_vector, metadata)

        # 測試查詢
        results = client.query_vector(test_vector, n_results=1)
        return JsonResponse({"connected": True, "results": results})

    except Exception as e:
        return JsonResponse({"connected": False, "error": str(e)})
