import os
import re
import shutil
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

import pdfplumber
from docx import Document
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from utils import extract_pdf_pages_as_chunks
from embedding import embedText
from my_chroma_utils import addDocuments


# Download necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download('punkt_tab')

# ============ CONFIG ============ #
# UNSORTED_DIR = r"c:\Users\FUNANANI NEKHUNGUNI\Desktop\test_docs"
# SORTED_DIR = r"c:\Users\FUNANANI NEKHUNGUNI\Desktop\smart_clusters"
FILE_PATH = ""
NUM_CLUSTERS = 10
SAMPLE_DOCS_PER_CLUSTER = 3
MAX_SUMMARY_LENGTH = 40  # for flan-t5-small
# ================================ #

# -------- Load Models -------- #
print("🔄 Loading models...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
summarizer = pipeline("text2text-generation", model="google/flan-t5-small", device=-1)
print("✅ Models ready.")


# -------- Read Files -------- #
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() or '' for page in pdf.pages])
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


documents = []
file_paths = []
def embed_and_save_to_chroma(FILE_PATH):
    print("📂 Reading file...")
    document = []
    file_path = []
    # for fname in os.listdir(UNSORTED_DIR):
    #     path = os.path.join(UNSORTED_DIR, fname)
    if  os.path.isfile(FILE_PATH):
    # return page numbers and page text
        doc_chunk = extract_pdf_pages_as_chunks(FILE_PATH)
        if doc_chunk:
            document.append(doc_chunk)
            file_path.append(FILE_PATH)

    print(f"📄 {len(document)} pages scanned loaded.")

    # -------- Embed Text -------- #
    print("📌 Embedding documents...")

    chunks = [chunk for doc in document for chunk in doc]
    print(f"📄 {len(chunks)} chunks  loaded.")
    # embeddings = embedder.encode(documents)
    # bundles the whole indexed page
    document_indexed = embedText(chunks, FILE_PATH)

    #save page and its indexes to chroa db
    print("📌 saving document pages to chroma db...")
    addDocuments(document_indexed)
    # print(document_indexed)
    return document_indexed

def scan_and_save_files_to_chroma(TARGET_DIR):
    
    scanned_files = []
    
    for fname in os.listdir(TARGET_DIR):
        path = os.path.join(TARGET_DIR, fname)
        if not os.path.isfile(path):
            continue
        # text = extract_text(path).strip()
        try:
            if path.endswith(".pdf"):
                scanned_files.append(f'{TARGET_DIR}/{fname}')
                page_indexed = embed_and_save_to_chroma(path)[0]
                if page_indexed:
                    documents.append(page_indexed)  # Truncate to 2000 chars
                    file_paths.append(path)
        except Exception as e:
            print(f"something went wrong , document not saved : {e}")

    print(f"📄 {len(documents)} documents loaded.")
    return scanned_files

def organize_files(UNSORTED_DIR , SORTED_DIR):
    for fname in os.listdir(UNSORTED_DIR):
        path = os.path.join(UNSORTED_DIR, fname)
        if not os.path.isfile(path):
            continue
        # text = extract_text(path).strip()
        try:
            if path.endswith(".pdf"):
                page_indexed = embed_and_save_to_chroma(path)[0]
                if page_indexed:
                    documents.append(page_indexed)  # Truncate to 2000 chars
                    file_paths.append(path)
        except Exception as e:
            print(f"something went wrong , document not saved : {e}")

    print(f"📄 {len(documents)} documents loaded.")

    if len(documents) > NUM_CLUSTERS :
        # -------- Embed Text -------- #
        print("📌 Loading Embedding documents...")
        # embeddings = embedder.encode(documents)
        embeddings = [doc["embedding"] for doc in documents]
        # -------- Cluster Embeddings -------- #
        print(f"🧠 Clustering into {NUM_CLUSTERS} groups...")
        kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42)
        labels = kmeans.fit_predict(embeddings)


        # -------- Organize by Cluster -------- #
        cluster_docs = defaultdict(list)
        cluster_files = defaultdict(list)

        for i, label in enumerate(labels):
            cluster_docs[label].append(documents[i])
            cluster_files[label].append(file_paths[i])


        # -------- Summarize Each Cluster -------- #
        print("📝 Summarizing each cluster...")
        folder_names = {}

        def extract_two_keywords(text):
            tokens = word_tokenize(text.lower())
            words = [word for word in tokens if word.isalpha()]
            filtered = [word for word in words if word not in stopwords.words('english')]
            unique = list(dict.fromkeys(filtered))  # remove duplicates, keep order
            return "_".join(unique[:2]) if len(unique) >= 2 else "_".join(unique)

        for label, docs in cluster_docs.items():
            sample_text = " ".join(doc["text"] for doc in docs[:SAMPLE_DOCS_PER_CLUSTER])
            sample_text = sample_text[:1000]  # keep it shorter for flan-t5-small
            prompt = f"Summarize the following text:\n{sample_text}"

            try:
                summary = summarizer(prompt, max_new_tokens=MAX_SUMMARY_LENGTH, do_sample=False)[0]['generated_text']
                short_name = extract_two_keywords(summary)
                folder_names[label] = short_name if short_name else f"Cluster_{label}"
            except Exception as e:
                print(f"⚠️ Summarization failed for cluster {label}: {e}")
                folder_names[label] = f"Cluster_{label}"


        # -------- Move Files into Named Folders -------- #
        print("📦 Organizing files into folders...")
        os.makedirs(SORTED_DIR, exist_ok=True)

        def safe_folder_name(name, max_len=100):
            name = re.sub(r'[<>:"/\\|?*]', '', name)
            return name.strip()[:max_len]

        for label, files in cluster_files.items():
            folder_name = safe_folder_name(folder_names[int(label)])
            folder_path = os.path.join(SORTED_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            for path in files:
                shutil.move(path, os.path.join(folder_path, os.path.basename(path)))

        print("✅ All files sorted and summarized into folders!")
    else:
        print(f"Faild to sort , number of cluster > documents")

