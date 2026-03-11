ARCHITECTURE OVERVIEW
Agentic RAG Chatbot
Hackathon Submission  ·  2026
1. System Overview
This system is a document-grounded Q&A chatbot built around a Retrieval-Augmented Generation (RAG) pipeline. Users upload files through a web interface, which are immediately chunked, embedded, and stored in a local ChromaDB vector database. Questions are answered by retrieving the most semantically relevant chunks and grounding the response in that context — with inline citations pointing back to source documents. A persistent memory subsystem extracts high-signal facts from each conversation and writes them to structured markdown files.

Technology Stack

Frontend	Single-page HTML/CSS/JS — drag-and-drop upload, chat UI, citation rendering

API Layer	FastAPI (Python) — /upload and /chat endpoints with Pydantic validation

Embeddings	sentence-transformers / all-MiniLM-L6-v2 — local, no external API required

Vector DB	ChromaDB (persistent) — cosine similarity retrieval, top-k chunks

Generation	Mistral-7B-Instruct-v0.2 via HuggingFace InferenceClient

Memory	LLM-extracted facts written to USER_MEMORY.md and COMPANY_MEMORY.md

2. Feature A — File Upload & RAG Pipeline
The ingestion and retrieval flow is the core of the system. Every uploaded document is immediately processed and made query-able.

Ingestion Flow

1	File Upload	POST /upload receives file via FastAPI. Validated against allowed extensions (.pdf, .txt, .docx).
2	Text Extraction	Plain text files read directly. PDFs parsed with pypdf, extracting text page by page.
3	Chunking	Text split into 500-character chunks with 50-character overlap using a sliding window to preserve context across boundaries.
4	Embedding	Each chunk encoded by all-MiniLM-L6-v2 into a 384-dimensional dense vector.
5	Indexing	Chunks, embeddings, and metadata (source filename, chunk index) stored in ChromaDB persistent collection.

Retrieval & Generation Flow

1	Query Embedding	User question encoded into the same 384-dim vector space as the indexed chunks.
2	Similarity Search	ChromaDB returns top-3 chunks by cosine similarity. Falls back gracefully if collection is empty.
3	Prompt Assembly	Retrieved chunks injected into a strict grounding prompt: 'Answer using ONLY the context below.'
4	Generation	Mistral-7B generates a response constrained to the provided context. Temperature 0.3 for consistency.
5	Citations	Each retrieved chunk's metadata (source file, chunk index) returned alongside the answer.


3. Feature B — Persistent Memory
After every chat turn, the system runs a memory extraction pass using the same LLM. For only high-signal, reusable facts are written.

Memory Architecture

1	Extraction Prompt	The question + answer pair is sent to Mistral with a strict prompt requesting USER: or COMPANY: prefixed facts, or NONE.
2	Parsing	Response parsed line-by-line. NONE values and markdown formatting stripped. Facts classified by prefix.
3	Sensitivity Filter	Regex patterns block passwords, API keys, emails, SSNs, credit cards, and bearer tokens before writing.
4	Append	Surviving facts appended as bullet points to USER_MEMORY.md or COMPANY_MEMORY.md.

Memory Files

USER_MEMORY.md	User-specific facts: role, preferences, working style. E.g. 'User is a data engineer'

COMPANY_MEMORY.md	Org-wide reusable learnings from document content. E.g. 'ETL pipelines used for data ingestion'

Design Decisions & Tradeoffs

•	LLM-based extraction —  Using the LLM itself for extraction means nuanced judgment (e.g. recognizing implicit role mentions), but adds one extra API call per turn.
•	Privacy —  the prompt instructs the model to avoid secret
•	Plain markdown —  Both memory files are plain markdown, making them human-readable, git-diffable, and easy to inspect during judging.

4. What We Would Improve
•	Retrieval Failure Handling - the system detects an empty collection and falls back to a general-knowledge prompt. 
•	Conversation history — pass prior turns into the generation prompt for multi-turn coherence
•	Memory versioning — track when facts were added and allow updates rather than only appends
•	Feature C — Safe Python sandbox with Open-Meteo time series analysis via llm-sandbox

