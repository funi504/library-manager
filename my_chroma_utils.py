import subprocess
import os
import sys
import time
import requests
from uuid import uuid4
import chromadb
from chromadb.config import Settings

# Define port and path for Chroma DB
# CHROMA_PORT = "8000"
# CHROMA_PATH = "./chroma_db"
# CHROMA_HOST = "localhost"

# # Activate virtual environment check
# VENV_PYTHON = os.path.join(".", ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".", ".venv", "bin", "python")
# if sys.executable != os.path.abspath(VENV_PYTHON):
#     print("⚠️ Please activate your virtual environment first:")
#     print("Windows: .\\.venv\\Scripts\\activate")
#     print("Unix/Mac: source .venv/bin/activate")
#     sys.exit(1)

# # Start Chroma server in the background
# print(f"🚀 Starting ChromaDB server on port {CHROMA_PORT}...")

# server_process = subprocess.Popen(
#     ["chroma", "run", "--path", CHROMA_PATH, "--port", CHROMA_PORT],
#     stdout=subprocess.PIPE,
#     stderr=subprocess.PIPE
# )

# Wait until server is reachable
# def wait_for_server(host, port, timeout=30):
#     url = f"http://{host}:{port}/api/v1/heartbeat"
#     for _ in range(timeout):
#         try:
#             r = requests.get(url)
#             if r.status_code == 200:
#                 print("✅ ChromaDB server is up.")
#                 return True
#         except Exception as e:
#             print(e)
#             pass
#         time.sleep(1)
#     print("❌ Failed to connect to ChromaDB server.")
    
#     return False

# if not wait_for_server(CHROMA_HOST, CHROMA_PORT):
#     server_process.terminate()
#     sys.exit(1)

CHROMA_PATH = "./chroma_db"

chroma_client = chromadb.PersistentClient()

# Get or create the collection
collection = chroma_client.get_or_create_collection(name="documents")


def search_documents(query,embedder, top_k=5):
    query_embedding = embedder.encode(query)
    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k  # adjust how many results you want
    )
    # scores = cosine_similarity(query_embedding, embeddings)[0]
    # top_indices = np.argsort(scores)[::-1][:top_k]
    # for i in range(len(results["documents"])):
    #     print(f"Document: {results['documents'][i]}")
    #     print(f"Metadata: {results['metadatas'][i]}")
    #     print(f"Distance: {results['distances'][i]}")
    #     print("---")
    print(results)
    return results
# Add documents to ChromaDB
def addDocuments(document_indexed):
    print(f"{len(document_indexed)} to be added to chroma")
    
    for doc in document_indexed:
        id = str(uuid4())
        try:
            collection.add(
                documents=[doc["text"]],
                metadatas=[{
                    "file_path": doc["path"],
                    "page_number": doc["page"],
                    "chunk": doc["chunk"]
                }],
                ids=[id],
                embeddings=[doc["embedding"]]
            )
            
            # print(f"document id : {id}")
            # results = collection.get(ids=id)
            # print(results["documents"])
            # print(results["metadatas"])
        except Exception as e:
            print(f"falide to save document to chroma : {e}")
    
            

# # Example usage
# if __name__ == "__main__":
#     # Sample doc to test
#     documents = [
#         {
#             "text": "Hello Chroma!",
#             "path": "sample.txt",
#             "page": 1,
#             "chunk": 0,
#             "embedding": [0.1] * 1536  # must match your embedding size
#         }
#     ]
#     addDocuments(documents)
#     print("✅ Documents added to ChromaDB.")
