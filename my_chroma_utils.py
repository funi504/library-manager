import subprocess
import os
import sys
import time
import requests
from uuid import uuid4
import chromadb
from chromadb.config import Settings

# Define port and path for Chroma DB
CHROMA_PORT = "8000"
CHROMA_PATH = "./chroma_db"
CHROMA_HOST = "localhost"

# Activate virtual environment check
VENV_PYTHON = os.path.join(".", ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".", ".venv", "bin", "python")
if sys.executable != os.path.abspath(VENV_PYTHON):
    print("⚠️ Please activate your virtual environment first:")
    print("Windows: .\\.venv\\Scripts\\activate")
    print("Unix/Mac: source .venv/bin/activate")
    sys.exit(1)

# Start Chroma server in the background
print(f"🚀 Starting ChromaDB server on port {CHROMA_PORT}...")

server_process = subprocess.Popen(
    ["chroma", "run", "--path", CHROMA_PATH, "--port", CHROMA_PORT],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait until server is reachable
def wait_for_server(host, port, timeout=30):
    url = f"http://{host}:{port}/api/v1/heartbeat"
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("✅ ChromaDB server is up.")
                return True
        except Exception as e:
            print(e)
            pass
        time.sleep(1)
    print("❌ Failed to connect to ChromaDB server.")
    
    return False

# if not wait_for_server(CHROMA_HOST, CHROMA_PORT):
#     server_process.terminate()
#     sys.exit(1)

# Connect to Chroma HTTP client
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))

# Get or create the collection
collection = chroma_client.get_or_create_collection(name="documents")

# Add documents to ChromaDB
def addDocuments(document_indexed):
    for doc in document_indexed:
        collection.add(
            documents=[doc["text"]],
            metadatas=[{
                "file_path": doc["path"],
                "page_number": doc["page"],
                "chunk": doc["chunk"]
            }],
            ids=[str(uuid4())],
            embeddings=[doc["embedding"]]
        )

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
