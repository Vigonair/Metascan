import fitz  # PyMuPDF
import re
import spacy
# 1. We import the Category Logic here
from metascan.enrich import extract_keywords_tfidf, assign_category,clean_text

# Load spaCy safely
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# ---------------------------------------------------------
# 1. HELPER: Extract Layout Blocks
# ---------------------------------------------------------
def extract_layout_blocks(file_path):
    doc = fitz.open(file_path)
    blocks = []
    # Check first 2 pages max
    for i, page in enumerate(doc):
        if i > 1: break
        raw_blocks = page.get_text("dict")["blocks"]
        for b in raw_blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        blocks.append({
                            "text": span["text"].strip(),
                            "size": span["size"],
                            "y": span["bbox"][1],
                            "x": span["bbox"][0]
                        })
    doc.close()
    return blocks

# ---------------------------------------------------------
# 2. TITLE DETECTION (Metadata + Visual Fallback)
# ---------------------------------------------------------
def detect_title_metadata(file_path):
    """
    Tweak: Check internal PDF metadata first!
    """
    try:
        with fitz.open(file_path) as doc:
            meta_title = doc.metadata.get("title", "").strip()
            
            # Filter out bad/generic titles
            if not meta_title: return None
            if len(meta_title) < 5: return None
            if "microsoft word" in meta_title.lower(): return None
            if "untitled" in meta_title.lower(): return None
            
            return meta_title
    except:
        return None

def detect_title_visual(blocks):
    """
    Fallback: Find the text with the LARGEST font size.
    """
    valid_blocks = [b for b in blocks if len(b["text"]) > 2]
    if not valid_blocks: return "", 0

    max_size = max(b["size"] for b in valid_blocks)
    
    # Get all text with that Max Font Size
    title_parts = [b for b in valid_blocks if b["size"] >= max_size - 1]
    title_parts.sort(key=lambda b: b["y"])
    
    full_title = " ".join([b["text"] for b in title_parts])
    last_title_y = title_parts[-1]["y"]
    
    return full_title, last_title_y

# ---------------------------------------------------------
# 3. AUTHOR DETECTION (Positional Strategy)
# ---------------------------------------------------------
def detect_authors(blocks, title_bottom_y):
    # If title_bottom_y is 0 (metadata title), scan top 250px
    start_y = title_bottom_y if title_bottom_y > 0 else 0
    end_y = start_y + 250

    candidates = [
        b for b in blocks 
        if b["y"] > start_y 
        and b["y"] < end_y
        and len(b["text"]) > 2
    ]
    candidates.sort(key=lambda b: (b["y"], b["x"]))
    
    author_text = " ".join([b["text"] for b in candidates])
    
    # --- CLEANING ---
    author_text = re.sub(r"\S+@\S+", "", author_text)
    
    # Remove academic junk words (Including 'Manuscript', 'Published')
    junk_pattern = r"\b(University|Dept|Department|School|Institute|Received|Accepted|Abstract|Correspondence|Author|Public Access)\b.*"
    author_text = re.sub(junk_pattern, "", author_text, flags=re.IGNORECASE)

    authors = []
    # 1. spaCy Detection
    if nlp:
        doc = nlp(author_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) > 1:
                name = ent.text.strip()
                if "manuscript" not in name.lower():
                    authors.append(name)
    
    # 2. Regex Fallback
    if not authors:
        regex_names = re.findall(r"\b[A-Z][a-z]*\.?\s[A-Z][a-z]+\b", author_text)
        authors = [n for n in regex_names if "Manuscript" not in n and "Published" not in n]

    return list(set(authors))

# ---------------------------------------------------------
# 4. MAIN ENTRY POINT
# ---------------------------------------------------------
def extract_pdf_data_visual(file_path):
    """
    Main function used by Upload Page.
    """
    blocks = extract_layout_blocks(file_path)
    
    # A. Try Metadata Title
    title = detect_title_metadata(file_path)
    title_y = 0 
    
    # B. Fallback to Visual Title
    if not title:
        title, title_y = detect_title_visual(blocks)
    
    # C. Last Resort: Filename
    if not title:
        title = file_path.split("/")[-1].replace(".pdf", "")

    # D. Detect Authors
    authors = detect_authors(blocks, title_y)
    
    # E. Content
    full_text = " ".join([b["text"] for b in blocks])
    match = re.search(r"Abstract[:\s]*(.*?)Introduction", full_text, re.IGNORECASE | re.DOTALL)
    raw_abstract = match.group(1).strip() if match else full_text[:600]

    abstract = clean_text(raw_abstract)
    
    # F. Year
    year = 0
    year_match = re.findall(r"\b(?:19|20)\d{2}\b", full_text)
    if year_match:
        year = max([int(y) for y in year_match if 1990 <= int(y) <= 2026])
    
    # G. Enrichment (RESTORED!)
    keywords = extract_keywords_tfidf(abstract)
    category = assign_category(abstract)  # <--- Calculates "Biomedical"

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "year": year,
        "keywords": keywords,
        "category": category, # <--- Returns it to the app
        "full_text": full_text
    }

def extract_arxiv_id(text):
    match = re.search(r"arxiv:\s*(\d+\.\d+)", text, re.IGNORECASE)
    return match.group(1) if match else ""