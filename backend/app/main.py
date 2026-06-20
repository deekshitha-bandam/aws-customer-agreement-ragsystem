import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config, database, pdf_processor, embeddings, rag
from app.models import AskRequest, AskResponse, SourceChunk, IngestResponse

app = FastAPI(title="AWS Agreement RAG Q&A API")

# Allow React frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# We keep the FAISS index and the text chunks in memory so we don't have to reload them from disk on every request.
faiss_index = None
text_chunks = None

# Runs once when the server starts
@app.on_event("startup")
def startup_event():
    database.init_db()

    global faiss_index, text_chunks
    faiss_index, text_chunks = embeddings.load_index_and_chunks()

    if faiss_index is not None:
        print(f"Loaded existing index from disk with {len(text_chunks)} chunks.")
    else:
        print("No saved index found yet. Call POST /ingest first.")

# Post endpoint to ingest the PDF and build the FAISS index: Extract text, create embeddings, and save to disk.
@app.post("/ingest", response_model=IngestResponse)
def ingest_document():
    global faiss_index, text_chunks

    try:
        chunks = pdf_processor.load_and_chunk_pdf()

        if not chunks:
            raise HTTPException(status_code=500, detail="No text could be extracted from the PDF.")

        chunk_embeddings = embeddings.create_embeddings(chunks)
        index = embeddings.build_faiss_index(chunk_embeddings)
        embeddings.save_index_and_chunks(index, chunks)

        # update our in-memory copies so /ask can use them right away
        faiss_index = index
        text_chunks = chunks

        return IngestResponse(
            message="PDF processed and indexed successfully.",
            num_chunks=len(chunks)
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"PDF file not found at {config.PDF_PATH}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

# ask endpoint to answer a question using the RAG pipeline, and log the interaction to SQLite
@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if faiss_index is None or text_chunks is None:
        raise HTTPException(
            status_code=400,
            detail="No document has been ingested yet. Call POST /ingest first."
        )

    start_time = time.time()

    try:
        answer, sources, answer_found = rag.answer_question(request.question, faiss_index, text_chunks)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the LLM (is Ollama running?). Error: {str(e)}"
        )

    response_time_ms = int((time.time() - start_time) * 1000)

    database.log_query(
        question=request.question,
        answer=answer,
        answer_found=answer_found,
        response_time_ms=response_time_ms
    )

    return AskResponse(
        answer=answer,
        sources=[SourceChunk(chunk_id=s["chunk_id"], text=s["text"]) for s in sources],
        answer_found=answer_found,
        response_time_ms=response_time_ms
    )

# analytics endpoint to return usage statistics from the SQLite logs table
@app.get("/analytics")
def get_analytics():
    return {
        "most_frequent_questions": database.get_most_frequent_questions(),
        "unanswered_queries": database.get_unanswered_queries(),
        "average_response_time_ms": database.get_average_latency(),
        "total_queries": database.get_total_query_count(),
    }


@app.get("/")
def root():
    """Just a friendly landing message so hitting the base URL isn't a 404."""
    return {"message": "AWS Agreement RAG API is running. See /docs for the API docs."}