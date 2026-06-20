from pathlib import Path

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
PDF_PATH = PROJECT_ROOT / "data" / "aws_customer_agreement.pdf"
DATA_DIR = PROJECT_ROOT / "data"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index.bin"
CHUNKS_PATH = DATA_DIR / "chunks.json"
DB_PATH = DATA_DIR / "usage_logs.db"

# PDF Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Embeddings model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# RAG Retrieval
TOP_K = 3

# If even the best match is > 1.2: "not found"
# instead of forcing the LLM to hallucinate.
MAX_DISTANCE_THRESHOLD = 1.2

# LLM (Ollama) model
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2:0.5b"
OLLAMA_TIMEOUT = 60  # seconds

# Analytics
ANALYTICS_LIMIT_FREQUENT = 10
ANALYTICS_LIMIT_UNANSWERED = 20