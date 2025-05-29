from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from manager import embedder

def search_documents(query, documents, file_paths, embeddings, top_k=5):
    query_embedding = embedder.encode([query])
    scores = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    print(f"🔍 Top {top_k} matches for: '{query}'\n")
    for idx in top_indices:
        print(f"📄 File: {file_paths[idx]}")
        print(f"   🔗 Match Score: {scores[idx]:.4f}")
        print(f"   📝 Preview: {documents[idx][:200].replace('\n', ' ')}\n")
