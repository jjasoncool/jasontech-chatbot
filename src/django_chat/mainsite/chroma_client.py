# mainsite/chroma_client.py
import uuid
import chromadb
from django.conf import settings

class ChromaDBClient:
    def __init__(self):
        # 使用 HttpClient 連接遠程 ChromaDB 服務
        self.client = chromadb.HttpClient(host=settings.CHROMADB_URL)
        self.collection = self.client.get_or_create_collection(name="text_vectors")

    def insert_vector(self, vector, metadata):
        """插入向量和元數據到 ChromaDB"""
        unique_id = str(uuid.uuid4())  # 生成唯一 ID
        self.collection.add(
            ids=[unique_id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=["sample document"]
        )

    def query_vector(self, query_vector, n_results=5):
        """查詢相似向量"""
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return results
