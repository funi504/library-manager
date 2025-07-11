import webview
import os
from tkinter import filedialog, Tk
from manager import organize_files, embedder, scan_and_save_files_to_chroma
from my_chroma_utils import search_documents

class Api:
    def choose_directory(self):
        # Open native file dialog
        root = Tk()
        root.withdraw()  # Hide the main window
        folder_path = filedialog.askdirectory(title="Select Folder with Documents")
        root.destroy()

        if folder_path:
            print(f"📁 User selected: {folder_path}")
            scan_and_save_files_to_chroma(folder_path)
            return f"✅ Processed: {os.path.basename(folder_path)}"
        else:
            return "❌ No folder selected."

    def search_for_documents(self, querry): 
        results = search_documents(query=querry, embedder=embedder)

        # Flatten the first list level
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        formatted = []
        for doc_text, meta, score in zip(documents, metadatas, distances):
            formatted.append({
                "text": doc_text[:1000],
                "file_path": meta.get("file_path", "unknown"),
                "page_number": meta.get("page_number", "N/A"),
                "score": round(score, 4)
            })

        return formatted


               
if __name__ == "__main__":
    api = Api()
    webview.create_window("Smart Document Sorter", "index.html", js_api=api)
    webview.start()