# mainsite/services.py
from sentence_transformers import SentenceTransformer
from .chroma_client import ChromaDBClient

# 使用 lazy loading 進行初始化
_embedding_model = None
_chroma_client = None

def get_embedding_model():
    """加載並返回嵌入模型（如果尚未加載）"""
    global _embedding_model
    if _embedding_model is None:
        try:
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully!")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            _embedding_model = None
    return _embedding_model

def get_chroma_client():
    """初始化並返回 ChromaDB 客戶端（如果尚未初始化）"""
    global _chroma_client
    if _chroma_client is None:
        try:
            _chroma_client = ChromaDBClient()
            print("ChromaDB client initialized successfully!")
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            _chroma_client = None
    return _chroma_client
