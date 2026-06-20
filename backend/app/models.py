from pydantic import BaseModel, Field
from typing import List, Optional

# What the frontend sends us when the user asks a question.
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question")

# ne piece of supporting text we used to build the answer.
class SourceChunk(BaseModel):
    chunk_id: int
    text: str

# What we send back after answering a question.
class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    answer_found: bool  # True if we found relevant content, False if we said "not in document"
    response_time_ms: int

# What we send back after processing the PDF.
class IngestResponse(BaseModel):
    message: str
    num_chunks: int

# Send a erro response
class ErrorResponse(BaseModel):
    detail: str