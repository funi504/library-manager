from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from my_chroma_utils import collection

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def search_documents(query, top_k=5):
    query_embedding = embedder.encode(query)
    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k  # adjust how many results you want
    )
    # scores = cosine_similarity(query_embedding, embeddings)[0]
    # top_indices = np.argsort(scores)[::-1][:top_k]
    for i in range(len(results["documents"])):
        print(f"Document: {results['documents'][i]}")
        print(f"Metadata: {results['metadatas'][i]}")
        print(f"Distance: {results['distances'][i]}")
        print("---")
    
    return results

ids = ["22d12a0e-2a90-47fd-9bd8-fb8f4d34ca00"]
results = collection.get(ids=ids)

print(results["documents"])
print(results["metadatas"])

search_documents("Designed, developed, and maintained RESTful APIs using Python and Django, ensuring high availability")