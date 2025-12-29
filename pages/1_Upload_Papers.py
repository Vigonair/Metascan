import streamlit as st
from metascan.storage import save_pdf_permanently
from metascan.db import add_paper

# 1. VISUAL EXTRACTOR
from metascan.pdf_extractor import extract_pdf_data_visual, extract_arxiv_id
from metascan.arxiv_metadata import fetch_arxiv_metadata

# 2. VECTOR ENGINE
# (Make sure this matches your filename: embedding.py or embeddings.py)
from metascan.embeddings import generate_embedding

st.title("📤 Upload Research Papers")

# -----------------------------
# Upload PDF (VISUAL STRATEGY)
# -----------------------------
st.subheader("Upload PDF File")
pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

if pdf_file:
    # 1. Save PDF permanently
    st.info("Saving PDF permanently...")
    pdf_path = save_pdf_permanently(pdf_file)

    st.info("Analyzing Layout (Visual Strategy)...")
    
    # 2. Run the Visual Extractor
    # Returns: {'title', 'authors', 'abstract', 'year', 'keywords', 'category', 'full_text'}
    extracted = extract_pdf_data_visual(pdf_path)
    
    # 3. Check for arXiv Authority
    arxiv_id = extract_arxiv_id(extracted["full_text"])
    meta = {}
    if arxiv_id:
        st.success(f"arXiv ID detected: {arxiv_id}. Fetching authoritative metadata...")
        meta = fetch_arxiv_metadata(arxiv_id)

    # 4. Merge: Authority > Visual Heuristic
    final_title = meta.get("title") or extracted["title"]
    final_authors = meta.get("authors") or extracted["authors"]
    final_year = meta.get("year") or extracted["year"]
    final_journal = meta.get("journal") or "Unknown"

    # 5. Generate Vector Embedding
    st.info("Generating AI Embeddings...")
    text_to_embed = f"{final_title} {extracted['abstract']}"
    vector = generate_embedding(text_to_embed)

    # 6. Prepare Data for MongoDB
    paper_data = {
        "title": final_title,
        "authors": final_authors,
        "year": final_year,
        "journal": final_journal,
        "abstract": extracted["abstract"],
        "keywords": extracted["keywords"], 
        "tags": extracted["keywords"], 
        
        # 👇 THIS WAS MISSING! IT SAVES "Biomedical" / "AI" TO DB
        "category": extracted.get("category", "General"),
        
        "file_path": pdf_path,
        "embedding": vector,
        "uploaded_by": st.session_state.get("username", "Unknown")
    }

    inserted_id = add_paper(paper_data)

    st.success("PDF stored permanently and indexed ✅")
    
    # Show the category we found
    st.info(f"🏷️ Category Assigned: **{paper_data['category']}**")

    st.write("Paper ID:", inserted_id)
    
  
    # Debug info to see what we found
    with st.expander("See Extracted Metadata"):
        st.write(f"**Title:** {final_title}")
        st.write(f"**Authors:** {final_authors}")
        st.write(f"**Year:** {final_year}")
        st.write(f"**Abstract Snippet:** {extracted['abstract'][:200]}...")