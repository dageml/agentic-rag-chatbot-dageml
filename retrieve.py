import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documents"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query, k=3):

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return results["documents"][0], results["metadatas"][0]
