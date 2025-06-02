
# from manager import organize_files,embedder
# from my_chroma_utils import search_documents

# organize_files()
# search_documents("How to write research", embedder=embedder)
import customtkinter as ctk
import threading
from tkinter import messagebox
from manager import organize_files, embedder
from my_chroma_utils import search_documents

# Optional: setup nltk
import nltk
nltk.download('punkt')
nltk.download('stopwords')

ctk.set_appearance_mode("Dark")  # Modes: "Dark", "Light"
ctk.set_default_color_theme("blue")  # Other options: green, dark-blue

class DocOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("📁 SmartDoc Organizer")
        self.geometry("800x600")
        self.resizable(False, False)

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        self.tab_organize = self.tabview.add("Organize Files")
        self.tab_search = self.tabview.add("Search Documents")

        self.build_organize_tab()
        self.build_search_tab()

    def build_organize_tab(self):
        self.org_label = ctk.CTkLabel(self.tab_organize, text="📄 Organize your documents by topic", font=("Segoe UI", 20))
        self.org_label.pack(pady=20)

        self.org_button = ctk.CTkButton(self.tab_organize, text="Start Organizing", command=self.run_organize_thread)
        self.org_button.pack(pady=10)

        self.org_status = ctk.CTkLabel(self.tab_organize, text="", text_color="gray", wraplength=700)
        self.org_status.pack(pady=10)

    def build_search_tab(self):
        self.search_label = ctk.CTkLabel(self.tab_search, text="🔍 Search documents", font=("Segoe UI", 20))
        self.search_label.pack(pady=20)

        self.search_entry = ctk.CTkEntry(self.tab_search, width=400, placeholder_text="Type your query here...")
        self.search_entry.pack(pady=10)

        self.search_button = ctk.CTkButton(self.tab_search, text="Search", command=self.run_search_thread)
        self.search_button.pack(pady=5)

        self.search_results = ctk.CTkTextbox(self.tab_search, width=700, height=300, font=("Segoe UI", 12), wrap="word")
        self.search_results.pack(pady=20)

    def run_organize_thread(self):
        thread = threading.Thread(target=self.organize_files_safe)
        thread.start()

    def organize_files_safe(self):
        try:
            self.org_status.configure(text="⏳ Organizing files... Please wait.")
            organize_files()
            self.org_status.configure(text="✅ Files successfully organized!")
        except Exception as e:
            self.org_status.configure(text=f"❌ Error: {e}")

    def run_search_thread(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Input Needed", "Please enter a search query.")
            return
        thread = threading.Thread(target=self.search_documents_safe, args=(query,))
        thread.start()

    def search_documents_safe(self, query):
        try:
            self.search_results.delete("1.0", "end")
            self.search_results.insert("end", f"🔍 Searching for: {query}\n\n")

            raw_results = search_documents(query, embedder=embedder)  # Returns a tuple
            print("DEBUG: raw_results =", raw_results) 
            results = raw_results[0]  # Extract the actual results dictionary

            if not results["documents"]:
                self.search_results.insert("end", "❌ No results found.")
                return

            for i in range(len(results["documents"])):
                self.search_results.insert("end", f"🔹 Document {i + 1}:\n")
                self.search_results.insert("end", f"📄 Text: {results['documents'][i][:300]}...\n")
                self.search_results.insert("end", f"📑 Metadata: {results['metadatas'][i]}\n")
                self.search_results.insert("end", f"📏 Distance: {results['distances'][i]}\n")
                self.search_results.insert("end", "-" * 40 + "\n\n")

        except Exception as e:
            self.search_results.insert("end", f"❌ Error: {e}")


if __name__ == "__main__":
    app = DocOrganizerApp()
    app.mainloop()
