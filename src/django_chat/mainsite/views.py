# Create your views here.
from django.shortcuts import render
import json, requests
import nltk
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadFile
from .serializers import UploadedFileSerializer
from .services import get_embedding_model, get_chroma_client
from .visualization import visualize_vectors

from django.http import JsonResponse

nltk.download('punkt')
nltk.download('punkt_tab')

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

            # 過濾掉內容為 null 的項目
            json_content = [item for item in json_content if item.get('content') is not None]
            batch_size = 10  # 設定批次大小

            for idx, item in enumerate(json_content):
                content = item.get('content', '')
                url = item.get('url', 'N/A')
                title = item.get('title', 'N/A')

                if content:
                    sentences = nltk.sent_tokenize(content)  # 切分句子
                    vectors_batch = []
                    metadata_batch = []
                    documents_batch = []

                    for i in range(0, len(sentences), batch_size):
                        batch = sentences[i:i + batch_size]
                        vectors = model.encode(batch)  # 批量轉換句子為向量

                        # 收集向量、元數據和文件
                        vectors_batch.extend(vectors)
                        metadata_batch.extend([{"url": url, "title": title, "content": sentence} for sentence in batch])
                        documents_batch.extend(batch)

                        # 每處理完一個批次，插入向量資料
                        if len(vectors_batch) >= batch_size:
                            client.insert_multiple_vectors(vectors=vectors_batch, metadatas=metadata_batch, documents=documents_batch)
                            vectors_batch = []
                            metadata_batch = []
                            documents_batch = []

                    # 插入最後一批向量
                    if vectors_batch:
                        client.insert_multiple_vectors(vectors=vectors_batch, metadatas=metadata_batch, documents=batch)

                # 回報每筆 JSON 條目已處理
                print(f"Processed item {idx + 1}/{len(json_content)}: {title}")
                request.session.modified = True  # 更新 session 狀態以防止超時

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
        keyword = request.GET.get('keyword', '')
        if keyword != '':
            results = client.list_vectors(n_results=n_results, query_texts=keyword)
        else:
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


def query_ollama(request):
    # 從請求中獲取用戶問題
    question = request.GET.get('question', '')
    if not question:
        return JsonResponse({"error": "No question provided"}, status=400)

    # 使用遠端伺服器上的 Ollama API
    try:
        response = requests.post(
            "http://ollama:11434/v1/completions",  # 使用您驗證過的 URL
            json={
                "model": "llama3.2-vision",  # 使用您已驗證的模型名稱
                "prompt": question
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        ollama_response = response.json()
        print(ollama_response)

        # 提取並返回 Ollama 的回答
        choices = ollama_response.get("choices", [])
        if choices:
            answer = choices[0].get("text", "No response from Ollama.")
        else:
            answer = "No response from Ollama."

        return JsonResponse({"ollama_answer": answer})
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
