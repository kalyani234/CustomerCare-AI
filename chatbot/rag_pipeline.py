
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_MIN_SIMILARITY = 0.35

_model = None


# Load company documents
def load_documents():
    """Load all TXT documents from the project data directory."""
    data_dir = Path(__file__).resolve().parent.parent / "data"

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    documents = []

    for file_path in sorted(data_dir.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8").strip()

        if content:
            documents.append(content)

    if not documents:
        raise FileNotFoundError(
            f"No non-empty TXT documents found in {data_dir}"
        )

    return documents


# Split documents into chunks
def split_into_chunks(documents, chunk_size=500, overlap=50):
    """Split documents into overlapping text chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks = []
    step = chunk_size - overlap

    for document in documents:
        if not isinstance(document, str) or not document.strip():
            continue

        document = document.strip()

        for start in range(0, len(document), step):
            chunk = document[start:start + chunk_size].strip()

            if chunk:
                chunks.append(chunk)

    return chunks


# Load embedding model once
def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


# Cache document embeddings
@lru_cache(maxsize=4)
def get_document_embeddings(chunks):
    model = get_embedding_model()

    return model.encode(
        list(chunks),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )


# Semantic retrieval
def retrieve_relevant_chunks(
    question,
    chunks,
    top_k=3,
    min_similarity=DEFAULT_MIN_SIMILARITY
):
    if not isinstance(question, str) or not question.strip():
        return []

    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    if not isinstance(min_similarity, (int, float)):
        raise ValueError("min_similarity must be a number")

    if not -1 <= min_similarity <= 1:
        raise ValueError("min_similarity must be between -1 and 1")

    if not chunks:
        return []

    valid_chunks = [
        chunk for chunk in chunks
        if isinstance(chunk, str) and chunk.strip()
    ]

    if not valid_chunks:
        return []

    model = get_embedding_model()

    question_embedding = model.encode(
        [question.strip()],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )[0]

    document_embeddings = get_document_embeddings(
        tuple(valid_chunks)
    )

    similarity_scores = np.dot(
        document_embeddings,
        question_embedding
    )

    ranked_indices = np.argsort(similarity_scores)[::-1]

    relevant_chunks = []

    for index in ranked_indices:
        score = float(similarity_scores[index])

        if score >= min_similarity:
            relevant_chunks.append(valid_chunks[index])

        if len(relevant_chunks) >= top_k:
            break

    return relevant_chunks
