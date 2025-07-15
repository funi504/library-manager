import webview
import os
import platform
from tkinter import filedialog, Tk
from history_manager import init_db, add_to_history, get_history
from manager import organize_files, embedder, scan_and_save_files_to_chroma
from my_chroma_utils import search_documents,collection

init_db()

class Api:
    # choose dir to scan
    def choose_directory(self):
        # Open native file dialog
        root = Tk()
        root.withdraw()  # Hide the main window
        folder_path = filedialog.askdirectory(title="Select Folder with Documents")
        root.destroy()

        if folder_path:
            print(f"📁 User selected: {folder_path}")
            scanned_files = scan_and_save_files_to_chroma(folder_path)
            
            #add scanned files un a history tab under the folder it belongs to
            add_to_history(folder_path=folder_path , scanned_files=scanned_files)
            
            return f"✅ Processed: {os.path.basename(folder_path)}"
        else:
            return "❌ No folder selected."

    #search for information
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
            
        formatted.sort(key=lambda x: x["score"], reverse=True)
        return formatted

    def get_history(self):
        return get_history()
      
    def open_file(self, path):
        try:
            # path = os.path.normpath(path)

            if platform.system() == "Windows":
                
                # safe_path = os.path.normpath(path)
                print(path)
                os.system(f'start "" "{path}"') 
            else:
                return {"status": "error", "message": "This feature is only implemented for Windows."}

            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
                 
if __name__ == "__main__":
    api = Api()
    webview.create_window("Smart Document Sorter", "index.html", js_api=api)
    webview.start()