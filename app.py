
from manager import organize_files,embedder
from my_chroma_utils import search_documents

organize_files()
search_documents("How to write research", embedder=embedder)