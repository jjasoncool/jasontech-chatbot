# mainsite/visualization.py
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def visualize_vectors(vectors, metadatas, documents, output_path='static/visualization.png'):
    if not vectors:
        raise ValueError("No vectors to visualize")

    # 將列表轉換為 NumPy 數組
    vectors = np.array(vectors)

    # 打印調試信息
    print(f"Number of vectors: {len(vectors)}")
    print(f"Shape of vectors: {vectors.shape}")
    print(f"Vectors: {vectors}")

    # 將三維數組轉換為二維數組
    if vectors.ndim == 3:
        vectors = vectors.reshape(-1, vectors.shape[-1])

    # 設置 perplexity 值，確保小於樣本數量且至少為 1
    n_samples = len(vectors)
    if n_samples < 2:
        raise ValueError("Not enough samples to visualize")

    perplexity = min(30, n_samples - 1)

    # 使用 t-SNE 進行降維
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    reduced_vectors = tsne.fit_transform(vectors)

    # 繪製散點圖
    plt.figure(figsize=(10, 10))
    plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1], c='blue', alpha=0.5, label="Document Points")

    # 添加標籤
    for i, doc in enumerate([d for sublist in documents for d in sublist]):
        print(f"Document: {i}")
        doc = doc.replace('$', '\u0024')  # 處理特殊字符，直接替換
        doc_label = doc[:15] + "..." if len(doc) > 15 else doc  # 縮短長標籤

        # 使用 i 確保標籤對應正確的點
        plt.annotate(doc_label, (reduced_vectors[i, 0], reduced_vectors[i, 1]),
                     xytext=(5, 2), textcoords='offset points', fontsize=8, alpha=0.7)

    plt.title('ChromaDB Vectors Visualization')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')

    # 保存圖形為文件
    plt.savefig(output_path)
    plt.close()
