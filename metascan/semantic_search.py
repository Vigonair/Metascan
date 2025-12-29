import numpy as np
from metascan.db import get_all_papers
from metascan.embeddings import generate_embedding


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def semantic_search(query: str, top_k: int = 5):
    """
    Perform semantic search over stored paper embeddings.
    """
    query_embedding = generate_embedding(query)
    if not query_embedding:
        return []

    papers = get_all_papers()
    results = []

    for paper in papers:
        emb = paper.get("embedding", [])
        if not emb:
            continue

        score = cosine_similarity(query_embedding, emb)
        results.append((score, paper))

    # Sort by similarity score (descending)
    results.sort(key=lambda x: x[0], reverse=True)

    return results[:top_k]

def search_similar_papers(query: str, top_k: int = 5):
    """
    Finds papers based on meaning.
    """
    # 1. Convert user query to vector
    query_embedding = generate_embedding(query)
    if not query_embedding:
        return []

    # 2. Get all papers from DB
    papers = get_all_papers()
    results = []

    # 3. Compare them
    for paper in papers:
        emb = paper.get("embedding", [])
        if not emb: 
            continue

        score = cosine_similarity(query_embedding, emb)
        
        # Only keep positive matches
        if score > 0.0:
            paper["score"] = score
            results.append(paper)

    # 4. Sort by highest score
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]
