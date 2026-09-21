"""
Chroma & VectorStore Database Manager
Authored by @Arijit Dutta
"""
import os
from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

# Try Chroma import first, fallback to FAISS if needed
try:
    from langchain_community.vectorstores import Chroma
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

from langchain_community.vectorstores import FAISS

class VectorStoreManager:
    """Manages creation, indexing, and retrieval from Vector Store (Chroma/FAISS)."""
    
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vector_db = None
        self.persist_directory = os.getenv("PERSIST_DIR", "./data/chroma_db")

    def create_vector_db(self, documents: List[Document], collection_name: str = "scribe_bot"):
        """Create and populate vector database from list of document chunks."""
        if HAS_CHROMA:
            try:
                # Ensure directory exists
                os.makedirs(self.persist_directory, exist_ok=True)
                self.vector_db = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=collection_name
                )
                return self.vector_db
            except Exception as e:
                # Fall back to in-memory FAISS store if Chroma faces environment/C++ binding issues
                print(f"[VectorStoreManager] Chroma notice ({e}). Falling back to FAISS.")
        
        self.vector_db = FAISS.from_documents(documents, self.embeddings)
        return self.vector_db

    def get_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """Return retriever interface for top-k document lookup."""
        if self.vector_db is None:
            raise ValueError("Vector DB has not been initialized. Please index a YouTube video URL first.")
        return self.vector_db.as_retriever(search_kwargs={"k": k})

    def clear(self):
        """Reset current vector DB reference."""
        self.vector_db = None
