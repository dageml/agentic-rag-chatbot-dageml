import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from pypdf import PdfReader


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documents"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text, chunk_size=500, overlap=50):

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    print(f"Text chunked into {len(chunks)} chunks")
    print(chunks[:2])  # Print the first 2 chunks for verification
    return chunks


def ingest_document(file_path):
    path = Path(file_path)
    if path.suffix == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        

    chunks = chunk_text(text)

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    embeddings = embedding_model.encode(chunks).tolist()

    ids = [f"{file_path}_chunk_{i}" for i in range(len(chunks))]

    metadatas = [
        {"source": file_path, "chunk": i}
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"Ingested {len(chunks)} chunks")

if __name__ == "__main__":
    ingest_document("sample_docs/sample.txt")

