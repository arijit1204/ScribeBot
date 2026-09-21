"""
Groq LLM Integration Module
Authored by @Arijit Dutta
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

def get_groq_llm(api_key: str = None, model_name: str = None) -> ChatGroq:
    """Instantiate and return ChatGroq model instance."""
    load_dotenv(override=True)
    
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in your .env file.")
        
    model = model_name or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "900"))
    
    return ChatGroq(
        api_key=key,
        model=model,
        temperature=0.2,
        max_tokens=max_tokens
    )
