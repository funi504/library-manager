# 🧠 AI-Powered Desktop Assistant 

(for more AI assistant app - https://github.com/funi504/chatbot/blob/master/llm.py)

This project is a **local-first AI desktop assistant** built with Python. It combines an intuitive GUI powered by **PyWebView** with advanced AI models (from Hugging Face and SentenceTransformers) to enable **natural language understanding**, **semantic search**, and **memory recall** — all without needing to send your data to the cloud.

---

## 🌟 What This Project Does

- Loads a lightweight AI assistant into a native desktop window (no browser needed).
- Uses **transformers**, **sentence embeddings**, and **ChromaDB** to provide:
  - Text generation
  - Semantic search
  - Conversational memory
- Lets users ask questions or give commands in plain English.
- Can be compiled into a **single executable** for easy distribution across machines.

---

## 🧩 Technologies Used

| Tool             | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| **PyWebView**     | Displays a web-based UI in a native window                             |
| **PyInstaller**   | Packages everything into one distributable `.exe`                      |
| **SentenceTransformers** | Converts input into dense vector embeddings for semantic meaning |
| **Transformers (Hugging Face)** | Powers language understanding and generation              |
| **ChromaDB**      | Stores and searches vector representations of past user inputs         |

---

## ❓ Problem It Solves

Most AI apps today require:

- An internet connection
- Access to remote servers (with potential privacy concerns)
- Running in a browser or third-party platform

This project solves that by:

✅ Running entirely **offline**  
✅ Giving you **full control** of the data  
✅ Letting you **build and ship** your own private AI assistant as a desktop app

---

## 🚀 Getting Started (Development Mode)

### 1. Clone the Repo

