"""
Pydantic Request & Response Schemas
Authored by @Arijit Dutta
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message sender role ('user' or 'assistant')")
    content: str = Field(..., description="Message text content")

class IndexRequest(BaseModel):
    youtube_url: str = Field(..., description="Full YouTube video URL or ID")

class IndexResponse(BaseModel):
    status: str = "success"
    message: str
    video_id: str
    youtube_url: str
    summary: str
    chunks_indexed: int

class QueryRequest(BaseModel):
    question: str = Field(..., description="User question about the indexed video")
    chat_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation history")

class QueryResponse(BaseModel):
    status: str = "success"
    answer: str
    chat_history: List[ChatMessage]

class ClearResponse(BaseModel):
    status: str = "success"
    message: str = "Indexing context cleared successfully."

class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "SCRIBE BOT"
    author: str = "@Arijit Dutta"
