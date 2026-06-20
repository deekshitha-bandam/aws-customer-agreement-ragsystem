# RAG System - AWS Customer Agreement Q&A

A Retrieval-Augmented Generation (RAG) system that answers questions about the AWS Customer Agreement document. Built with FastAPI (backend), React (frontend), FAISS (vector search), and Ollama (local LLM).

## What This Does

This system allows users to:
- Upload and process a PDF document (AWS Customer Agreement)
- Ask questions about the document in natural language
- Get answers backed by relevant document excerpts
- View the source text chunks that were used to generate each answer
- Track usage analytics (most common questions, unanswered queries, response times)

Example:
- User asks: "How are fees and charges billed?"
- System finds relevant sections about billing
- Returns: "Fees are billed based on... [answer]. See source chunk 23."

## Quick Start (5 Minutes)

### Prerequisites

Install these on your machine:
- Python 3.10 or higher (https://www.python.org/downloads/)
- Node.js 16 or higher (https://nodejs.org/)
- Ollama (https://ollama.com)

### Setup Instructions

Clone and enter the repository:
```bash
git clone https://github.com/deekshitha-bandam/aws-customer-agreement-ragsystem.git
cd aws-customer-agreement-ragsystem
```

Open three terminal windows and run these commands (one in each):

Terminal 1 - Start Ollama (the local LLM):
```bash
ollama serve
```

While Terminal 1 is running, in another terminal pull the model:
```bash
ollama pull qwen2:0.5b
```

Terminal 2 - Start the FastAPI backend:
```bash
cd aws-customer-agreement-ragsystem/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see: "Uvicorn running on http://0.0.0.0:8000"

Terminal 3 - Start the React frontend:
```bash
cd aws-customer-agreement-ragsystem/frontend
npm install
npm run dev
```

You should see: "VITE v... ready" and a URL like http://localhost:5173

### Test It

1. Open http://localhost:5173 in your browser
2. Click "1. Ingest Document (run this first)"
3. Wait for "Done! Processed the document into 94 chunks"
4. Go to "Ask a Question" tab
5. Type: "How are fees and charges billed?"
6. Click "Ask" and see the answer with source chunks
7. Go to "Analytics Dashboard" to see usage stats

That's it! The system is working.

### Populate Test Data (Optional)

To test the analytics with multiple questions:
```bash
cd aws-customer-agreement-ragsystem/backend
python test_queries.py
```

This sends 35 test questions and populates the analytics dashboard.

## Architecture Overview

### System Components

```
User Browser (React)
        |
        |-- HTTP Requests --
        |
FastAPI Backend (Python)
        |
        +----- RAG Pipeline -----
        |         |
        |         +-- PDF Processor (parse and chunk text)
        |         +-- Embeddings (sentence-transformers)
        |         +-- Vector Store (FAISS index)
        |         +-- LLM Interface (Ollama)
        |
        +----- Data Layer -----
                  |
                  +-- SQLite Database (logging and analytics)
```

### Data Flow for Answering a Question

1. User types question in browser
2. Frontend sends POST /ask request to backend
3. Backend processes:
   - Embeds the question (turns it into numbers)
   - Searches FAISS index for 3 most similar document chunks
   - Checks if chunks are relevant (similarity threshold)
   - If relevant: builds a prompt with the chunks
   - If not relevant: skips LLM call, returns "not in document"
   - Sends prompt to Ollama (local LLM)
   - Ollama generates an answer
4. Backend logs question/answer/metadata to SQLite
5. Frontend receives answer and displays it with source chunks
6. Analytics dashboard queries SQLite for stats

### File Structure

```
rag-project/
├── README.md                    (This file)
├── requirements.txt             
├── backend/
│   ├── app/
│   │   ├── main.py             FastAPI server with 3 endpoints
│   │   ├── rag.py              RAG pipeline (retrieve and generate)
│   │   ├── embeddings.py       FAISS vector store management
│   │   ├── pdf_processor.py    PDF text extraction and chunking
│   │   ├── database.py         SQLite setup and analytics queries
│   │   ├── models.py           Pydantic validation models
│   │   ├── config.py           Settings (chunk size, thresholds, etc.)
│   │   └── __init__.py
│   ├── data/
│   │   └── aws_customer_agreement.pdf 
│   └── test_queries.py          Script to populate test data
└── frontend/
|    ├── src/
    │   ├── App.jsx              Main React component
    │   ├── AskPage.jsx          Q&A chat interface
    │   ├── AnalyticsPage.jsx    Analytics dashboard
    │   ├── App.css              Styling
    │   ├── config.js            Backend URL configuration
    │   └── main.jsx
    ├── package.json             Node.js dependencies
    ├── vite.config.js           Vite build configuration
    └── index.html
```

## Key Design Decisions

### 1. Chunking Strategy (800 chars with 150 char overlap)

Why 800 characters?
- AWS Customer Agreement clauses are typically 500-900 characters
- 800 characters keeps most complete clauses in a single chunk
- This ensures related information stays together for better context

Why 150 character overlap?
- 150 characters is approximately one sentence
- Prevents cutting sentences across chunk boundaries
- Ensures context is not lost at chunk edges
- Small enough to keep index size manageable

Alternative considered: Sentence-based chunking
- Problem: Some legal sentences span 200+ characters
- Problem: Sentence boundaries do not align with semantic meaning
- Our approach: Character count respects semantic units better

### 2. Embeddings (sentence-transformers, all-MiniLM-L6-v2)

Why sentence-transformers?
- Free (no API keys required)
- Runs locally on CPU (fast enough for this use case)
- 100MB model size (easy to download)
- Produces 384-dimensional vectors (good balance of speed and quality)
- Specifically trained for semantic similarity tasks

Why all-MiniLM-L6-v2 specifically?
- Smallest model from the SBERT library that maintains high quality
- Fast inference time (less than 100ms for 94 chunks)
- Excellent performance on semantic search benchmarks

Alternative considered: OpenAI embeddings
- Problem: Requires API key and internet connection
- Problem: Costs money per request
- Problem: Cannot run locally
- Our choice: Local-first for accessibility

### 3. Vector Store (FAISS IndexFlatL2)

Why FAISS (Facebook AI Similarity Search)?
- Fast (C++ backend)
- Lightweight (no separate server needed)
- Flexible (many index types available)

Why IndexFlatL2 (brute-force search)?
- We have 94 chunks (small dataset)
- Exact search is fast enough (less than 10ms)
- Simple to understand and explain
- No training required (unlike IVF or HNSW)

For larger datasets (more than 100k chunks):
- Would consider HNSW (approximate nearest neighbor)
- Trades small accuracy loss for 100x speed improvement
- Still compatible with our code

### 4. Relevance Threshold (distance <= 1.2)

FAISS uses L2 (Euclidean) distance:
- Lower distance = more similar
- Distance 0 = identical
- Distance 1.0 = somewhat similar
- Distance 2.0+ = quite different

Why 1.2?
- Tested empirically with the AWS Agreement
- Questions in the document: typically 0.3-0.8
- Irrelevant questions (e.g., "What is the weather?"): typically 1.5+
- 1.2 is a safe threshold that prevents hallucination

What happens at threshold?
- If best match distance > 1.2: Skip LLM call
- Return: "I could not find this information in the document"
- This prevents the LLM from making up answers

### 5. Top-K Chunks (3 chunks per query)

Why 3 chunks?
- 3 chunks times 800 chars = 2400 characters of context
- Approximately 3-4 dense legal paragraphs
- Enough detail to answer most questions
- Small enough that prompts stay focused

Why not more?
- Longer prompts = slower LLM inference (2-5 sec vs 5-15 sec)
- More context can introduce noise or contradiction
- Top-3 are usually sufficient for document Q&A

Calculation:
- Each chunk: approximately 800 chars
- 3 chunks: approximately 2400 chars
- For comparison: A typical ChatGPT prompt is 1000-4000 chars
- Our 2400 chars is a good balance

### 6. LLM Choice (Ollama plus qwen2:0.5b)

Why Ollama?
- Runs completely locally (no internet required after setup)
- No API keys needed
- Free (open source)
- Works on any machine (Mac, Windows, Linux)
- Good for student and developer environments

Why qwen2:0.5b?
- Lightweight model (0.5B parameters) suitable for local deployment.
- Low memory and compute requirements, runs efficiently on standard hardware.
- Fast inference speed, providing quick response times.

Response time expectations:
- First token: 0.5-1 second (slower)
- Subsequent tokens: approximately 100-200ms per token
- 50-token answer: 5-10 seconds typical
- On GPU: 2-3 seconds typical

Alternative considered: GPT-4 or Claude API
- Problem: Requires API key
- Problem: Costs money
- Problem: Internet required
- Our choice: Local-first for accessibility

### 7. Database (SQLite)

Why SQLite?
- Single file (no server installation needed)
- Zero configuration
- Fast for small datasets (less than 1M rows)
- Included with Python
- Perfect for logging and analytics use cases

Schema design:
```sql
CREATE TABLE query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,           -- Full user question
    answer TEXT NOT NULL,              -- Generated response
    answer_found INTEGER NOT NULL,     -- 1=found, 0=not found
    response_time_ms INTEGER NOT NULL, -- Latency in milliseconds
    created_at TEXT NOT NULL           -- ISO timestamp
);
```

Why include answer_found?
- Lets us compute "unanswered queries" statistic
- Helps identify gaps in document coverage
- Single bit of info, huge analytical value

Queries exposed:
1. Most frequent questions: GROUP BY plus COUNT
2. Unanswered queries: WHERE answer_found=0
3. Average latency: AVG(response_time_ms)
4. Total count: COUNT(*)

Alternative considered: PostgreSQL
- Problem: Requires separate server
- Problem: More setup complexity
- Our choice: SQLite sufficient and simpler

### 8. Frontend (React plus Vite)

Why React?
- Component-based (clean, maintainable)
- State management (simple with useState)
- Large ecosystem (helpful for scaling)
- Show full-stack competency

Why Vite (not Create React App)?
- Faster build and reload times
- Simpler configuration
- Modern JavaScript tooling
- Easier to deploy

Why plain CSS (not Tailwind or Material)?
- Demonstrates CSS knowledge
- Smaller bundle size
- Full control over styling
- Easier to understand and modify

Architecture:
- App.jsx: Main component, tab navigation, ingest button
- AskPage.jsx: Chat interface, question history, source display
- AnalyticsPage.jsx: Stats cards, frequency table, unanswered table
- No routing library (simple useState for tabs)
- No UI framework (just plain React plus CSS)

### 9. No External APIs

Design principle: Local-first
- Ollama runs locally
- sentence-transformers runs locally
- FAISS runs locally
- SQLite runs locally
- React frontend runs locally

Benefits:
- Works without internet (after initial setup)
- No API costs
- No rate limits
- No dependency on external services
- No privacy concerns (data stays local)

Constraints:
- Setup requires downloading models
- First ingest takes 10-30 seconds
- Slower than cloud LLMs
- Quality depends on local hardware

### 10. Error Handling Strategy

HTTP Status Codes:
- 200: Success
- 400: Bad request (empty question, no document ingested)
- 422: Validation error (Pydantic)
- 503: Service unavailable (Ollama not running)
- 500: Internal server error (other)

Every error response includes:
- Meaningful error message (not stack trace)
- Actionable guidance (e.g., "Is Ollama running?")
- User-friendly language (no technical jargon)

Example error:
```json
{
  "detail": "No document has been ingested yet. Call POST /ingest first."
}
```

Not:
```
FileNotFoundError: [Errno 2] No such file or directory: 'faiss_index.bin'
```

## API Reference

### POST /ingest
Processes the PDF and builds the FAISS index.

Request: (no body needed)
```bash
curl -X POST http://localhost:8000/ingest
```

Response:
```json
{
  "message": "PDF processed and indexed successfully.",
  "num_chunks": 94
}
```

### POST /ask
Answers a question using the RAG pipeline.

Request:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How are fees billed?"}'
```

Response:
```json
{
  "answer": "Fees are billed monthly based on... [full answer]",
  "sources": [
    {
      "chunk_id": 42,
      "text": "Relevant text from the document..."
    },
    {
      "chunk_id": 15,
      "text": "More relevant text..."
    }
  ],
  "answer_found": true,
  "response_time_ms": 3200
}
```

### GET /analytics
Returns usage analytics from SQLite.

Request:
```bash
curl http://localhost:8000/analytics
```

Response:
```json
{
  "most_frequent_questions": [
    {"question": "how are fees billed?", "times_asked": 5},
    {"question": "what is the payment term?", "times_asked": 3}
  ],
  "unanswered_queries": [
    {"question": "What is the weather?", "asked_at": "2026-06-19T10:30:00"}
  ],
  "average_response_time_ms": 3400,
  "total_queries": 35
}
```

## Testing

### Run Manual Test Queries
```bash
cd aws-customer-agreement-ragsystem/backend
python test_queries.py
```

This sends 35 realistic test questions:
- 30 questions that should be answered from the document
- 5 questions that are out of scope (should be flagged "not found")

## Troubleshooting

### "Could not reach the backend"
- Check FastAPI is running: http://localhost:8000/
- Check port 8000 is available
- Check no firewall blocking localhost

### "Could not reach Ollama"
- Verify ollama serve is running
- Check Ollama is listening on http://localhost:11434
- Verify model is pulled: ollama pull qwen2:0.5b

### "No document has been ingested yet"
- Click "Ingest Document" button
- Wait for "Done! Processed into 94 chunks" message
- Then go to "Ask a Question" tab

### "Wrong number or type of arguments for overloaded function"
- This was a bug in embeddings.py (now fixed)
- Delete old data: rm -f backend/data/*.bin backend/data/*.json
- Restart backend and try again

### "Too many query rows: 50001"
- FAISS index has memory limit on large queries
- Reduce TOP_K in config.py from 3 to 2
- Or reduce chunk overlap

## Performance Characteristics

Typical timings (on modest hardware):

First ingest:
- PDF extraction: 1-2 seconds
- Chunking: less than 1 second
- Creating embeddings: 5-15 seconds
- Building FAISS index: less than 1 second
- Total: 10-30 seconds

Per question:
- Embedding question: less than 100ms
- FAISS search: less than 10ms
- LLM inference: 2-5 seconds (depends on hardware)
- Database logging: less than 10ms
- Total: 2-5 seconds

Analytics queries:
- Most frequent: less than 50ms
- Unanswered: less than 50ms
- Average latency: less than 10ms
- Total count: less than 10ms

Scaling considerations:
- Current system: 94 chunks, less than 100ms search
- With 1M chunks: Would need approximate search (HNSW)
- With 100M chunks: Would need distributed system

## Questions?

See the full documentation in the outputs folder, or refer to inline code comments for detailed explanations of design decisions.
