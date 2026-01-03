import os
from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader,
    CSVLoader, UnstructuredExcelLoader,
    UnstructuredPowerPointLoader
)
from langchain_core.documents import Document


# --------------------------------------------------
# Resolve BASE directory safely
# ai_chatbot/app/utils/data_loader.py
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"


SUPPORTED_EXTENSIONS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader
}


def load_document(filepath: str) -> list[Document]:
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        print(f"⚠️ Unsupported file type: {ext}")
        return []

    loader_class = SUPPORTED_EXTENSIONS[ext]
    loader = loader_class(filepath)

    try:
        docs = loader.load()
        print(f"📄 Loaded {len(docs)} chunk(s) from: {os.path.basename(filepath)}")
        return docs
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return []


def load_all_documents(folder_path: Path | None = None) -> list[Document]:
    """
    Loads all supported files and returns LangChain Document objects.
    """

    folder = folder_path or DOCUMENTS_DIR

    if not folder.exists():
        print(f"⚠️ Documents folder not found: {folder}")
        return []

    all_docs: list[Document] = []

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            print(f"🔹 Processing: {file.name}")
            docs = load_document(str(file))
            all_docs.extend(docs)

    print(f"\n✅ Total documents loaded: {len(all_docs)}\n")
    return all_docs
