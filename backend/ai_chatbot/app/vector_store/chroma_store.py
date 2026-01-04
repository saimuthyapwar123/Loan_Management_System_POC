import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ai_chatbot.app.utils.data_loader import load_all_documents

VECTOR_PATH = "vector_store_chroma"

_embedding = None
_vector_db = None


def get_embedding():
    global _embedding
    if _embedding is None:
        _embedding = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
    return _embedding


def get_chroma_retriever(k: int = 3):
    """
    Lazy-safe Chroma retriever.
    This function is the ONLY place where:
    - documents are loaded
    - embeddings are created
    - Chroma is initialized
    """

    global _vector_db

    if _vector_db is not None:
        return _vector_db.as_retriever(search_kwargs={"k": k})

    print("🔹 Initializing Chroma vector store...")

    os.makedirs(VECTOR_PATH, exist_ok=True)

    embedding = get_embedding()

    documents = load_all_documents()

    # 🚨 SAFETY CHECK #1
    if not documents:
        print("⚠️ No documents found. Skipping vector DB creation.")
        return None

    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # 🚨 SAFETY CHECK #2
    if not texts:
        print("⚠️ No text chunks found. Skipping vector DB creation.")
        return None

    _vector_db = Chroma(
        persist_directory=VECTOR_PATH,
        embedding_function=embedding
    )

    # Insert only if empty (prevents duplicates)
    if _vector_db._collection.count() == 0:
        _vector_db.add_texts(texts=texts, metadatas=metadatas)
        _vector_db.persist()
        print("✅ Documents stored successfully in Chroma DB.")
    else:
        print("⚠️ Chroma DB already contains data — skipping insert.")

    return _vector_db.as_retriever(search_kwargs={"k": k})
