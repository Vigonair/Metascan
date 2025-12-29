import pandas as pd
from metascan.db import add_paper
# 👇 UPDATE: Import from the new "enrich.py" file
from metascan.enrich import extract_keywords_tfidf, assign_category

def import_csv(file_path: str):
    """
    Read a CSV file and insert each row as a paper into MongoDB.
    Uses 'enrich.py' to generate Category and Keywords.
    """

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return f"Error reading CSV: {e}"

    inserted_ids = []

    for _, row in df.iterrows():

        # Convert fields safely to strings
        title = str(row.get("title", ""))
        authors = str(row.get("authors", "")).split(",")
        # Clean up author names (remove extra whitespace)
        authors = [a.strip() for a in authors if a.strip()]
        
        year = row.get("year", 0)
        try:
            year = int(year)
        except:
            year = 0

        journal = str(row.get("journal", ""))
        abstract = str(row.get("abstract", ""))
        keywords_csv = str(row.get("keywords", "")).split(",")
        keywords_csv = [k.strip() for k in keywords_csv if k.strip()]

        # 👇 1. USE NEW KEYWORD EXTRACTOR
        extracted = extract_keywords_tfidf(abstract)
        
        # Merge CSV keywords + NLP keywords
        final_keywords = list(set(keywords_csv + extracted))

        # 👇 2. USE NEW CATEGORY CLASSIFIER (AI Brain)
        # This ensures CSV papers get a category like "Cybersecurity" or "AI"
        category = assign_category(abstract, title)

        paper_data = {
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "abstract": abstract,
            "keywords": final_keywords,
            "category": category, # 👈 Added Category
            "file_path": ""       # Empty since it is a CSV entry
        }

        # add_paper will automatically generate the Embedding! 🧠
        inserted_id = add_paper(paper_data)
        inserted_ids.append(inserted_id)

    return inserted_ids
