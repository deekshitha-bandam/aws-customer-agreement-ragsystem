from pypdf import PdfReader
from app import config

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    
    return text.strip()

#  Splits text into overlapping chunks.
def chunk_text(text, chunk_size, overlap):
    chunks = []
    step = chunk_size - overlap
    
    for start in range(0, len(text), step):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():  # Skip empty chunks
            chunks.append(chunk)
    
    return chunks

# Convenience function to load PDF and chunk it in one call
def load_and_chunk_pdf(pdf_path=None):
    if pdf_path is None:
        pdf_path = config.PDF_PATH
    
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    
    return chunks