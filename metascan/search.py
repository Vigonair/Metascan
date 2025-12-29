from metascan.db import papers_col
from bson.objectid import ObjectId


def search_by_text(query: str):
    """
    Basic regex search across title, abstract, and keywords.
    """
    return list(papers_col.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"abstract": {"$regex": query, "$options": "i"}},
            {"keywords": {"$regex": query, "$options": "i"}}
        ]
    }))


def search_by_author(author_name: str):
    """
    Search papers by author name.
    """
    return list(papers_col.find({
        "authors": {"$regex": author_name, "$options": "i"}
    }))


def search_by_year(year: int):
    """
    Search papers published in a specific year.
    """
    return list(papers_col.find({
        "year": year
    }))


def search_advanced(query="", author="", year=None):
    """
    Combined search filters.
    Allows searching by:
    - query text
    - author name
    - year

    This is what Streamlit UI will use.
    """

    search_filter = {}

    # Text search
    if query:
        search_filter["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"abstract": {"$regex": query, "$options": "i"}},
            {"keywords": {"$regex": query, "$options": "i"}},
            {"authors": {"$regex": query, "$options": "i"}}
        ]

    # Author filter
    if author:
        search_filter["authors"] = {"$regex": author, "$options": "i"}

    # Year filter
    if year:
        search_filter["year"] = int(year)

    return list(papers_col.find(search_filter))
