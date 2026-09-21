"""
FastAPI Server Entry Point for SCRIBE
Authored by @Arijit Dutta
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.schemas import (
    IndexRequest, IndexResponse, 
    QueryRequest, QueryResponse, 
    ClearResponse, HealthResponse, ChatMessage
)
from ai.pipelines.rag_pipeline import ScribePipeline

load_dotenv(BASE_DIR / ".env")

app = FastAPI(
    title="SCRIBE BOT API Server",
    description="Backend REST API serving SCRIBE BOT indexing, summarization, and QA",
    version="1.0.0"
)

# Configure CORS Middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Pipeline Singleton
pipeline = ScribePipeline()

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.post("/api/index", response_model=IndexResponse)
async def index_video(payload: IndexRequest):
    """
    Fetch YouTube transcript, process semantic chunks, build vector store, 
    and return video summary.
    """
    if not payload.youtube_url or not payload.youtube_url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="YouTube URL cannot be empty."
        )

    try:
        res = pipeline.index_video(payload.youtube_url.strip())
        return IndexResponse(
            status="success",
            message="Video indexed successfully ✅! You can now ask questions about the video.",
            video_id=res["video_id"],
            youtube_url=res["youtube_url"],
            summary=res["summary"],
            chunks_indexed=res["chunks_indexed"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing video: {str(e)}"
        )

@app.post("/api/query", response_model=QueryResponse)
async def query_video(payload: QueryRequest):
    """Answer question about indexed YouTube video using Groq RAG chain."""
    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question text cannot be empty."
        )

    try:
        answer, _ = pipeline.ask_question(payload.question.strip())
        
        # Build updated chat history
        updated_history = list(payload.chat_history or [])
        updated_history.append(ChatMessage(role="user", content=payload.question.strip()))
        updated_history.append(ChatMessage(role="assistant", content=answer))
        
        return QueryResponse(
            status="success",
            answer=answer,
            chat_history=updated_history
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )

@app.post("/api/clear", response_model=ClearResponse)
async def clear_index():
    """Clear active index and chat history."""
    try:
        pipeline.clear()
        return ClearResponse()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting index: {str(e)}"
        )

# Mount Frontend Static Files
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def read_root():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Frontend index.html not found"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    print(f"[SCRIBE] Starting Server at http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)

