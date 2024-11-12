# mainsite/chroma_client.py
import uuid
import chromadb
from django.conf import settings

class ChromaDBClient:
    def __init__(self):
        # 使用 HttpClient 連接遠程 ChromaDB 服務
        self.client = chromadb.HttpClient(host=settings.CHROMADB_URL)
        self.collection = self.client.get_or_create_collection(name="text_vectors")

    def insert_vector(self, vector, metadata, document):
        """插入向量和元數據到 ChromaDB"""
        unique_id = str(uuid.uuid4())  # 生成唯一 ID
        self.collection.add(
            ids=[unique_id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[document]
        )

    def insert_multiple_vectors(self, vectors, metadatas, documents):
        """插入多筆向量和元數據到 ChromaDB"""
        # print(f"Inserting {documents} into ChromaDB...")
        unique_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]  # 生成唯一 ID 列表
        self.collection.add(
            ids=unique_ids,
            embeddings=vectors,
            metadatas=metadatas,
            documents=documents
        )

    def query_vector(self, query_vector, n_results=5):
        """查詢相似向量"""
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return results

    def list_vectors(self, n_results=5, query_texts=None):
        """列出資料庫內有的前幾筆資料"""
        results = self.collection.query(
            query_texts=[query_texts] if query_texts else ["*"],
            n_results=n_results,
            # include=['embeddings', 'metadatas', 'documents']
        )
        return results

    def get_all_vectors(self):
        """提取所有向量和元數據"""
        results = self.collection.query(
            query_texts=["*"],  # 匹配所有文本
            n_results=1000,  # 設置提取的最大數量
            include=['embeddings', 'metadatas', 'documents']
        )
        vectors = results['embeddings']
        metadatas = results['metadatas']
        documents = results['documents']
        return vectors, metadatas, documents
