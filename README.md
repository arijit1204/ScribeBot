# 🎥⚡ SCRIBE BOT — AI YouTube Video Assistant

> **Transform long YouTube videos into interactive knowledge bases in real-time.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink)](https://python.langchain.com/)
[![Groq LLM](https://img.shields.io/badge/Groq_LLM-F05032?style=for-the-badge)](https://groq.com/)
[![Chroma DB](https://img.shields.io/badge/Chroma_Vector_DB-FF6F61?style=for-the-badge)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

**SCRIBE BOT** is an intelligent, high-performance Retrieval-Augmented Generation (RAG) platform that transforms unstructured YouTube video transcripts into interactive, searchable vector indexes. Powered by **LangChain**, **Groq's LLaMA/Qwen LLMs**, **HuggingFace Embeddings**, and **Chroma Vector DB**, SCRIBE BOT enables users to index videos instantly, receive automated AI summaries, and converse with video content in real-time through a sleek, YouTube-dark-themed web UI.

---

## ✨ Key Features

- 🎥 **YouTube Dark Mode UI**: Custom-built static HTML5/CSS3/JS interface styled to mirror YouTube Dark Mode, complete with live embedded video playback and quick suggestion chips.
- 🚀 **FastAPI Backend Architecture**: High-speed, async REST API server with structured request/response validation and CORS configuration.
- 📜 **Multi-Language Transcript Extraction**: Intelligent transcript processing supporting 14+ primary languages with automated fallback mechanisms.
- 🧠 **Context-Aware Semantic Chunking**: Overlapping chunk splitting (`chunk_size=512`, `chunk_overlap=256`) embedded with `sentence-transformers/all-MiniLM-L6-v2`.
- ⚡ **Groq LLM Acceleration**: Lightning-fast inference via Groq Cloud (`qwen/qwen3.8-27b` / `llama-3.3-70b-versatile`).
- 🔒 **Zero Data Leak Design**: Environment variables isolated via `.env`, strict `.gitignore` patterns, and no credentials committed to git.

---

## 📂 Project Architecture & Directory Structure

```text
TubeRAG/
├── PRD.md                 # Product Requirements Document
├── README.md              # Project documentation & GitHub guide
├── requirements.txt       # Pinned dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file (secures credentials & data)
├── frontend/              # YouTube-themed static web interface
│   ├── index.html         # Main application web layout
│   ├── css/
│   │   └── styles.css     # Custom YouTube dark theme stylesheet
│   └── js/
│       └── app.js         # Async REST client & UI state manager
├── backend/               # FastAPI REST server & API routes
│   ├── __init__.py
│   ├── schemas.py         # Pydantic data schemas
│   └── main.py            # FastAPI application entrypoint
├── ai/                    # Modular AI & RAG Engine
│   ├── __init__.py
│   ├── ingestion/         # YouTube transcript & caption loader
│   ├── processing/        # Text cleaning & time-aware chunking
│   ├── embeddings/        # HuggingFace MiniLM embeddings wrapper
│   ├── vectorstore/       # Chroma vector store manager
│   ├── retrieval/         # Similarity search retriever
│   ├── llm/               # Groq API client integration
│   ├── chains/            # LangChain Q&A chains & prompts
│   └── pipelines/         # RAG pipeline orchestrator
└── data/                  # Local vector storage & transcript cache (gitignored)
    └── .gitkeep
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- A **Groq API Key** (Get your free key from [Groq Console](https://console.groq.com/)).

### 2. Environment Setup

Clone or navigate to the repository directory:
```bash
git clone https://github.com/your-username/SCRIBE-BOT.git
cd SCRIBE-BOT
```

Create and activate a virtual environment:
```bash
# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

Install pinned dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and set your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
PERSIST_DIR=./data/chroma_db
HOST=0.0.0.0
PORT=8000
```

### 4. Run the Server

Start the FastAPI application:
```bash
python backend/main.py
```
*Alternatively, launch with Uvicorn live-reload:*
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Web Application

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🛰️ REST API Contract Reference

| Method | Endpoint | Description | Payload / Response |
|---|---|---|---|
| `POST` | `/api/index` | Index video transcript & generate summary | `{"youtube_url": "https://www.youtube.com/watch?v=..."}` |
| `POST` | `/api/query` | Perform vector similarity Q&A query | `{"question": "...", "chat_history": [...]}` |
| `POST` | `/api/clear` | Clear vector store & chat session | `{}` |
| `GET` | `/api/health` | Health check & system status | Returns `{"status": "ok", "app": "SCRIBE BOT"}` |

---

## 🔒 Security & Data Leak Prevention

This codebase adheres to strict security standards:
- ❌ **No Hardcoded Keys**: API keys are read strictly from environment variables.
- 🛡️ **Comprehensive `.gitignore`**: Secret `.env` files, `.venv` virtual environments, Chroma vector stores (`data/`), and system temp files are excluded from tracking.
- 🧪 **Verification**: Validated using automated regex scanners prior to publication.

---

## 👤 Author & License

Developed & Maintained by **@Arijit Dutta**  
Released under the **MIT License**.
