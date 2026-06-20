import requests
from app import config

# Retrieves the top-K most similar chunks from the FAISS index.
def retrieve_relevant_chunks(query, index, chunks):
    if index is None or not chunks:
        return [], False

    # Embed the query the same way we embedded the chunks
    from app.embeddings import embed_single_query
    query_embedding = embed_single_query(query)

    # Search FAISS for similar embeddings
    from app.embeddings import search_index
    distances, indices = search_index(index, query_embedding, config.TOP_K)


    relevant_chunks = []
    best_distance = distances[0] if len(distances) > 0 else float('inf')

    for dist, idx in zip(distances, indices):
        if idx == -1:
            continue
        relevant_chunks.append({
            "chunk_id": idx,
            "text": chunks[idx],
            "distance": dist
        })
    is_relevant = best_distance <= config.MAX_DISTANCE_THRESHOLD

    return relevant_chunks, is_relevant

# Constructs a prompt that tells the LLM to answer ONLY from the provided context.
def build_prompt(question, context_chunks):
    context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])

    prompt = f"""You are a helpful AI assistant answering questions about an AWS Customer Agreement document.

Below is the relevant text from the document:

{context_text}

Question: {question}

Instructions:
- Answer ONLY using the text provided above.
- If the answer cannot be found in the text, respond with: "I could not find this information in the provided document."
- Do not make up or infer information that isn't explicitly in the text.
- Be concise and direct."""

    return prompt

# Calls the Ollama LLM with the constructed prompt and returns the answer.
def call_ollama(prompt):
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/generate",
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=config.OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Could not reach Ollama at {config.OLLAMA_URL}. "
            "Is it running? Try: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise Exception(
            f"Ollama request timed out after {config.OLLAMA_TIMEOUT} seconds. "
            "Try asking a shorter question or check your hardware."
        )

# The main RAG pipeline orchestration function.
def answer_question(question, index, chunks):
    
    # Step 1: Retrieve relevant chunks
    relevant_chunks, is_relevant = retrieve_relevant_chunks(question, index, chunks)

    # Step 2: If not relevant, skip LLM call (save time + avoid hallucination)
    if not is_relevant:
        return (
            "I could not find information about this in the AWS Customer Agreement document.",
            [],
            False
        )

    # Step 3: Build prompt with context
    prompt = build_prompt(question, relevant_chunks)

    # Step 4: Call LLM
    answer = call_ollama(prompt)

    # Step 5: Check if the LLM explicitly said "not found"
    answer_found = "could not find" not in answer.lower()

    # Step 6: Format sources for response
    sources = [
        {"chunk_id": chunk["chunk_id"], "text": chunk["text"]}
        for chunk in relevant_chunks
    ]

    return answer, sources, answer_found