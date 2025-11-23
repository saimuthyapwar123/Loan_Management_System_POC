import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.utils.data_loader import load_all_documents

# --- Sample Knowledge Base ---
# documents = [
#     "Our company offers a 7-day refund policy on all products.",
#     "Customers can contact support via email or live chat.",
#     "We provide free shipping for orders above $50.",
#     "Technical support is available 24/7 for premium members."
# ]
documents = load_all_documents()


# --- Load a Pretrained Sentence Transformer Model ---
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Convert Each Document into an Embedding Vector ---
print("🔹 Generating embeddings for documents...")
doc_embeddings = model.encode(
    documents,
    convert_to_numpy=True,          # Convert output to numpy array
    show_progress_bar=True,         # Show progress for many docs
    normalize_embeddings=True       # Normalize for cosine similarity
)

# Convert embeddings to float32 for FAISS compatibility
doc_embeddings = doc_embeddings.astype('float32')
print(f"Generated {len(doc_embeddings)} document embeddings of size {doc_embeddings.shape[1]}")


# --- Initialize a FAISS Index ---
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add all document embeddings to the index.
index.add(np.array(doc_embeddings))
print(f"FAISS index created with {index.ntotal} document vectors.")

# -------- Save FAISS Index & Metadata ---------
SAVE_DIR = "vector_store"
os.makedirs(SAVE_DIR, exist_ok=True)

# Save FAISS index file
faiss.write_index(index, os.path.join(SAVE_DIR, "documents.index"))

# Save embeddings + document texts (metadata)
np.save(os.path.join(SAVE_DIR, "embeddings.npy"), doc_embeddings)
with open(os.path.join(SAVE_DIR, "documents.txt"), "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(doc.replace("\n", " ") + "\n---DOC-END---\n")

print("Saved FAISS index, embeddings, and documents successfully!")

def retrieve_docs(query: str, k: int = 3):
    """Retrieve top-k relevant documents."""
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    return [documents[int(i)] for i in indices[0]]
