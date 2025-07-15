# //

# get documents
# devide documents
# embed documents
# save documents in to chroma
# sort in to folders

# Persistence Directory
# If you want to persist data between app restarts, you must set the directory explicitly in the config:

# python
# Copy
# Edit
# from chromadb.config import Settings

# CHROMA_PATH = "./chroma_db"

# chroma_client = chromadb.Client(Settings(
#     persist_directory=CHROMA_PATH
# ))
# If you don’t do this, ChromaDB will store everything in memory, and all your data will be lost when the app closes.


#work on storing multiple pages

#chrome extension for recording articles and podcast to search for the information later