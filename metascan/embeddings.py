from sentence_transformers import SentenceTransformer

# Load once (important for performance)
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> list:
    """
    Generate a semantic embedding for given text.
    """
    if not text or not text.strip():
        return []

    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)

    return embedding.tolist()
