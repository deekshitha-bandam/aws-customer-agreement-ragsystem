import numpy as np
import faiss
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app import config

# Load the embedding model
print("Loading embedding model... (this happens once when the server starts)")
embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
print("Embedding model loaded.")

# Creates embeddings for a list of text chunks.
def create_embeddings(chunks):
    embeddings = embedding_model.encode(chunks, show_progress_bar=True)
    return embeddings.astype('float32')

# Builds a FAISS index from embeddings using IndexFlatL2 (brute-force search).
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]  # Should be 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Saves the FAISS index and chunks to disk.
def save_index_and_chunks(index, chunks):
    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    faiss.write_index(index, str(config.FAISS_INDEX_PATH))
    
    # Save chunks as JSON
    with open(config.CHUNKS_PATH, 'w') as f:
        json.dump(chunks, f)

# Loads the FAISS index and chunks from disk, if they exist.
def load_index_and_chunks():
    if not Path(config.FAISS_INDEX_PATH).exists() or not Path(config.CHUNKS_PATH).exists():
        return None, None

    index = faiss.read_index(str(config.FAISS_INDEX_PATH))

    with open(config.CHUNKS_PATH, 'r') as f:
        chunks = json.load(f)

    return index, chunks

# Embeds a single query string into a vector.
def embed_single_query(query):
    return embedding_model.encode([query], show_progress_bar=False).astype('float32')

# searches the FAISS index for the top-k nearest neighbors of a query embedding.
def search_index(index, query_embedding, top_k):
    distances, indices = index.search(query_embedding, top_k)
    return distances[0], indices[0]  # Return the first (and only) row