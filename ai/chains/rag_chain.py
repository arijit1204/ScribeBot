"""
LangChain RAG Chains & Prompt Engineering
Authored by @Arijit Dutta
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

SYSTEM_PROMPT = (
    "You are SCRIBE AI, an intelligent YouTube video assistant. "
    "Use the provided YouTube transcript context to answer questions accurately and concisely. "
    "Structure your answers cleanly using Markdown formatting, headers, bullet points, and code blocks where relevant. "
    "If the user asks for code examples or technical implementation details, provide clean, complete, working code. "
    "If the exact answer is not present in the context, explicitly state what information is available from the transcript. "
    "\n\nContext:\n{context}"
)

def build_rag_chain(llm, retriever):
    """Construct retrieval-augmented generation chain."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)
