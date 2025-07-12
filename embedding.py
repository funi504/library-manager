from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def split_text_into_chunks(text, max_words=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def embedText(chunks , path):
    divided_texts = []
    metadata = []
    
    for chunk in chunks:
        page_num = chunk["page_number"]
        text = chunk["text"]

        # Split the page text into ~300-word chunks
        sub_chunks = split_text_into_chunks(text, max_words=300)
        for i, sub_chunk in enumerate(sub_chunks):
            divided_texts.append(sub_chunk)
            metadata.append({
                "page_number": page_num,
                "chunk_number": i + 1
            })

    # Embed all 300-word sub-chunks
    embeddings = embedder.encode(divided_texts)

    # Bundle everything together
    page_indexed_embeddings = [
        {
            "page": metadata[i]["page_number"],
            "chunk": metadata[i]["chunk_number"],
            "embedding": embeddings[i],
            "text": divided_texts[i],
            "path":path.replace("\\", "/")
        }
        for i in range(len(embeddings))
    ]

    return page_indexed_embeddings

