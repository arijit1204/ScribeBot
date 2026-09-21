"""
Retriever Component Layer
Authored by @Arijit Dutta
"""
from typing import List
from langchain_core.documents import Document
from ..vectorstore.chroma_store import VectorStoreManager

def retrieve_relevant_chunks(vector_store_manager: VectorStoreManager, query: str, k: int = 5) -> List[Document]:
    """Search and return top k matching document chunks for a query."""
    retriever = vector_store_manager.get_retriever(k=k)
    if hasattr(retriever, "invoke"):
        return retriever.invoke(query)
    elif hasattr(retriever, "get_relevant_documents"):
        return retriever.get_relevant_documents(query)
    return []
