import arxiv

def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """
    Fetch authoritative metadata from arXiv.
    """
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())

        return {
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "year": paper.published.year,
            "journal": "arXiv"
        }
    except Exception:
        return {}
