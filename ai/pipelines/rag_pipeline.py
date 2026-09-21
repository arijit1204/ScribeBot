"""
SCRIBE High-Level Orchestrator Pipeline
Authored by @Arijit Dutta
"""
from typing import Dict, Any, Tuple, List
from ..ingestion.loader import load_youtube_transcript, extract_video_id
from ..processing.chunker import chunk_documents
from ..embeddings.embeddings import get_embeddings
from ..vectorstore.chroma_store import VectorStoreManager
from ..llm.groq_llm import get_groq_llm
from ..chains.rag_chain import build_rag_chain

class ScribePipeline:
    """Orchestrates end-to-end transcript extraction, indexing, summarization, and QA."""
    
    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_store_manager = VectorStoreManager(self.embeddings)
        self.current_video_id = None
        self.current_youtube_url = None
        self.summary_cache = None

    def index_video(self, youtube_url: str) -> Dict[str, Any]:
        """
        Process YouTube URL: fetch transcript, split chunks, index in vector DB,
        and generate video summary.
        """
        video_id = extract_video_id(youtube_url)
        raw_documents = load_youtube_transcript(youtube_url)
        
        if not raw_documents:
            raise ValueError("No transcript data could be fetched for this video.")

        # Split documents into chunks
        chunked_docs = chunk_documents(raw_documents, chunk_size=512, chunk_overlap=256)
        
        # Build Vector Store
        self.vector_store_manager.create_vector_db(chunked_docs, collection_name=f"yt_{video_id}")
        
        self.current_video_id = video_id
        self.current_youtube_url = youtube_url
        
        # Generate video summary using default prompt
        summary = self._generate_summary()
        self.summary_cache = summary
        
        return {
            "video_id": video_id,
            "youtube_url": youtube_url,
            "chunks_indexed": len(chunked_docs),
            "summary": summary,
            "status": "indexed"
        }

    def _generate_summary(self) -> str:
        """Helper to generate initial video summary."""
        try:
            answer, _ = self.ask_question("Summarize this video in detail with key takeaways.")
            return answer
        except Exception as e:
            return f"Video indexed successfully, but automated summary generation encountered an issue: {str(e)}"

    def ask_question(self, question: str) -> Tuple[str, List[Dict[str, str]]]:
        """Query indexed video vector store with user question via Groq RAG chain."""
        if not self.vector_store_manager.vector_db:
            raise ValueError("No video indexed. Please index a YouTube video URL first.")

        retriever = self.vector_store_manager.get_retriever(k=5)
        llm = get_groq_llm()
        rag_chain = build_rag_chain(llm, retriever)

        response = rag_chain.invoke({"input": question})
        
        if "answer" not in response:
            raise ValueError("LLM response did not contain an 'answer' field.")
            
        return response["answer"], []

    def clear(self):
        """Clear active index and session context."""
        self.vector_store_manager.clear()
        self.current_video_id = None
        self.current_youtube_url = None
        self.summary_cache = None
