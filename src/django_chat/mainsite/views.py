# Create your views here.
from django.shortcuts import render
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadFile
from .serializers import UploadedFileSerializer
from .services import get_embedding_model, get_chroma_client
from .visualization import visualize_vectors

from django.http import JsonResponse

class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        model = get_embedding_model()
        client = get_chroma_client()

        # 檢查是否成功加載模型和資料庫連接
        if model is None:
            return Response({"error": "Model could not be loaded."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if client is None:
            return Response({"error": "ChromaDB client could not be initialized."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        file_serializer = UploadedFileSerializer(data=request.data)

        if file_serializer.is_valid():
            file = request.FILES['file']
            file_content = file.read().decode('utf-8')
            json_content = json.loads(file_content)

            # 計算總句子數量
            total_sentences = sum(len(item.get('content', '').split('.')) for item in json_content)

            # 批量插入向量
            processed_sentences = 0
            batch_size = 10  # 設定批次大小
            vectors_batch = []
            metadata_batch = []
            documents_batch = []
            for item in json_content:
                content = item.get('content', '')

                if content:
                    sentences = content.split('.')

                    for i in range(0, len(sentences), batch_size):
                        batch = sentences[i:i + batch_size]
                        vectors = model.encode(batch)  # 批量轉換句子為向量

                        vectors_batch.extend(vectors)  # 收集向量
                        metadata_batch.extend([{"content": sentence} for sentence in batch])  # 收集元數據
                        documents_batch.extend(batch)  # 收集文件
                        processed_sentences += len(batch)

                        # 每處理完一個批次，插入向量資料
                        if len(vectors_batch) >= batch_size:
                            client.insert_multiple_vectors(vectors=vectors_batch, metadatas=metadata_batch, documents=documents_batch)
                            vectors_batch = []
                            metadata_batch = []
                            documents_batch = []

                        # 回報進度
                        progress = (processed_sentences / total_sentences) * 100
                        print(f"Progress: {progress:.2f}%")
                        request.session.modified = True

            # 插入最後一批向量
            if vectors_batch:
                client.insert_multiple_vectors(vectors=vectors_batch, metadatas=metadata_batch, documents=batch)


            # 儲存檔案資訊到資料庫
            file_instance = UploadFile(file=file)
            file_instance.save()

            return Response({"message": "File uploaded successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test_chromadb_connection(request):
    # 初始化 ChromaDB 客戶端
    client = get_chroma_client()

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



def query_chromadb(request):
    client = get_chroma_client()

    # 檢查是否成功初始化 ChromaDB 客戶端
    if client is None:
        return JsonResponse({"error": "ChromaDB client could not be initialized."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # 查詢 ChromaDB 內的所有資料
        n_results = int(request.GET.get('n_results', 10))  # 默認查詢 10 筆
        results = client.list_vectors(n_results=n_results)
        print(results)
        return JsonResponse({"results": results})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def visualize_chromadb(request):
    client = get_chroma_client()
    vectors, metadatas, documents = client.get_all_vectors()
    if not vectors:
        return render(request, 'visualization.html', {'error': 'No vectors to visualize'})

    output_path = 'static/visualization.png'
    visualize_vectors(vectors, metadatas, documents, output_path)

    output_path = output_path.replace('static/', '')

    return render(request, 'visualization.html', {'output_path': output_path})
