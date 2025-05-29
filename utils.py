import pdfplumber

def extract_pdf_pages_as_chunks(pdf_path):
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                chunks.append({
                    "page_number": i + 1,
                    "text": text.strip(),
                })
    return chunks

