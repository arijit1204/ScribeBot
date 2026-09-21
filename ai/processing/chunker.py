"""
Time-Aware and Recursive Character Chunker
Authored by @Arijit Dutta
"""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .cleaner import clean_transcript_text

def chunk_documents(
    documents: List[Document], 
    chunk_size: int = 512, 
    chunk_overlap: int = 256
) -> List[Document]:
    """
    Clean transcript content and split documents into overlapping chunks 
    preserving metadata.
    """
    cleaned_docs = []
    for doc in documents:
        cleaned_content = clean_transcript_text(doc.page_content)
        cleaned_docs.append(Document(
            page_content=cleaned_content,
            metadata=doc.metadata.copy()
        ))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    return splitter.split_documents(cleaned_docs)
