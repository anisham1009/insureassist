from pathlib import Path

import chromadb
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = BASE_DIR / "data" / "policy_documents"

CHROMA_DIR = BASE_DIR / "vectorstore"

VECTORIZER_PATH = CHROMA_DIR / "tfidf_vectorizer.pkl"


# ---------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


collection = chroma_client.get_or_create_collection(
    name="insurance_policies"
)


# ---------------------------------------------------------
# Load saved vectorizer
# ---------------------------------------------------------

def load_vectorizer():

    if not VECTORIZER_PATH.exists():

        raise FileNotFoundError(
            "TF-IDF vectorizer not found. "
            "Please run build_rag.py first."
        )

    return joblib.load(
        VECTORIZER_PATH
    )


# ---------------------------------------------------------
# Load policy documents
# ---------------------------------------------------------

def load_documents():

    documents = []
    ids = []
    metadatas = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        documents.append(text)

        ids.append(
            file_path.stem
        )

        metadatas.append(
            {
                "source": file_path.name
            }
        )

    return documents, ids, metadatas


# ---------------------------------------------------------
# Build vector database
# ---------------------------------------------------------

def build_vector_database():

    documents, ids, metadatas = load_documents()

    if not documents:

        raise ValueError(
            f"No policy documents found in "
            f"{DOCUMENTS_DIR}"
        )

    print(
        f"Found {len(documents)} policy documents."
    )

    # Create and fit TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
    )

    print("Creating TF-IDF embeddings...")

    vectors = vectorizer.fit_transform(
        documents
    ).toarray().tolist()

    # Make sure vectorstore directory exists
    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save vectorizer
    joblib.dump(
        vectorizer,
        VECTORIZER_PATH
    )

    print(
        f"Vectorizer saved to: {VECTORIZER_PATH}"
    )

    # Store documents and embeddings
    collection.upsert(
        documents=documents,
        embeddings=vectors,
        ids=ids,
        metadatas=metadatas,
    )

    print(
        f"Added {len(documents)} documents to ChromaDB."
    )


# ---------------------------------------------------------
# Search policies
# ---------------------------------------------------------

def search_policies(
    query: str,
    n_results: int = 3,
):

    vectorizer = load_vectorizer()

    query_vector = vectorizer.transform(
        [query]
    ).toarray().tolist()

    results = collection.query(
        query_embeddings=query_vector,
        n_results=n_results,
    )

    return results


# ---------------------------------------------------------
# Get relevant context
# ---------------------------------------------------------

def get_relevant_context(
    query: str,
    n_results: int = 3,
):

    results = search_policies(
        query,
        n_results,
    )

    documents = results["documents"][0]

    context = "\n\n".join(
        documents
    )

    return context