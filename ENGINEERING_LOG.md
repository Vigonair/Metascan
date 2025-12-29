# 📘 MetaScan Engineering Log

**Project:** MetaScan AI Indexer
**Status:** Phase 1 Complete
**Date:** December 2025

---

## 1. Overview
I am building an AI-powered search engine for research papers.
Phase 1 focused on the **Backend**, **Database**, and **Ingestion Pipeline**.

## 2. Tech Stack
* **Python 3.12**: Core logic
* **MongoDB**: NoSQL database for flexible metadata storage
* **Pandas**: For processing CSV data

## 3. Key Features Built
### A. Database Layer (`db.py`)
I implemented a singleton connection to MongoDB. The system can now:
- Connect to `metascan_db`
- Insert research papers via `add_paper()`
- Perform basic regex search

### B. NLP Pipeline (`nlp_pipeline.py`)
I created a custom NLP engine to auto-tag papers.
1. Cleans text (removes punctuation/numbers)
2. Extracts top keywords
3. Generates tags automatically

## 4. Code Snippet: The Fix
I faced an issue where CSV integers broke the string split function.
**The Fix:**
```python
# Forced conversion to string before splitting
"authors": str(row.get("authors", "")).split(",")

MetaScan Phase 2 Engineering Log
Project: MetaScan AI Indexer Version: v0.2 (Full Search & PDF Ingestion) Date: December 2025 Status: Phase 2 Complete

1. Executive Summary
Phase 2 transformed MetaScan from a simple database prototype into a functional Search & Retrieval System. We successfully implemented the Search Engine Logic, built a Multi-Page Streamlit UI, and integrated the core PDF Ingestion Pipeline. The system now supports end-to-end processing: uploading a raw PDF, extracting text/metadata, indexing it with AI tags, and retrieving it via a search interface.

2. Key Features Delivered
A. Advanced Search Engine (search.py)
Implemented a multi-filter search system using MongoDB native queries.

Capabilities:

Full-text search (Title, Abstract, Keywords).

Filter by Author.

Filter by Year.

Combined logic (Text + Author + Year) for precise retrieval.

B. PDF Ingestion Engine (pdf_extractor.py)
Integrated pdfplumber and PyPDF2 for robust document processing.

Extraction Logic:

Text: Full text extraction from all pages.

Title: Heuristic extraction from metadata or filename.

Abstract: Smart parsing (looks for "Abstract" keyword or grabs first 600 chars).

NLP Integration: Automatically runs the nlp_pipeline on extracted text to generate keywords and tags immediately upon upload.

C. Multi-Page User Interface (Streamlit)
Transformed the app into a professional multi-page application:

Home: Dashboard with total paper count metric.

Upload: Dual-mode support (CSV Batch Upload + Individual PDF Upload).

Search: Interactive search bar with result cards and "View Details" linking.

Paper Details: Dynamic page rendering full metadata, abstract, and tags for any selected paper.

3. Technical Architecture (Current State)
User Flow: Upload PDF (UI) → Save Temp File → Extract Text (pdf_extractor) → NLP Tagging → MongoDB Insert

Retrieval Flow: Search Query (UI) → MongoDB Regex Search → Result List → Click Detail → Fetch Document by ID

4. Code Highlight: The Search Logic
We implemented a flexible search function that constructs MongoDB queries dynamically based on user input.

Python

def search_advanced(query="", author="", year=None):
    search_filter = {}

    if query:
        search_filter["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"abstract": {"$regex": query, "$options": "i"}},
            {"keywords": {"$regex": query, "$options": "i"}},
        ]
    
    if author:
        search_filter["authors"] = {"$regex": author, "$options": "i"}

    return list(papers_col.find(search_filter))
5. Known Limitations & Future Roadmap (Post-Phase 2)
🔹 Current Limitations (To be improved in Phase 3)
Storage: PDFs are currently processed via a temporary file (uploaded_temp.pdf) and not permanently stored with unique IDs.

NLP Noise: Simple frequency-based extraction sometimes picks up non-keywords (e.g., "these", "paper").

Abstract Cleaning: The abstract extraction heuristic includes surrounding noise (e.g., "Abstract cybercriminals...").

Metadata Gaps: Author and Year extraction from PDFs is currently placeholder/manual, as PDF metadata is often missing these fields.

🚀 Future Roadmap (Phase 3 & Beyond)
Permanent Storage: Implement a proper uploads/pdfs/{uuid}.pdf storage system.

Smart NLP: Upgrade to spaCy or KeyBERT for semantic keyword extraction (removing noise).

PDF Viewing: Add an embedded PDF viewer or "Download" button in the Details page.

Analytics Upgrade: Visualize tag distribution and publication trends.

MetaScan Phase 3 Engineering LogProject: MetaScan AI IndexerVersion: v0.3 (Metadata-First Architecture & Analytics)Date: December 2025Status: Phase 3 Complete1. Executive SummaryPhase 3 marked a critical architectural pivot from "PDF Parsing" to a Metadata-First System. We integrated arXiv API as an authoritative source, implemented a robust NLP Text Normalization layer to fix PDF artifacts, and added a permanent storage strategy. Finally, we delivered a comprehensive Analytics Dashboard to visualize research trends, completing the core value loop of the application.2. Key Architectural DecisionsA. The "Metadata-First" PivotProblem: Heuristic extraction from PDFs (authors, years) proved unreliable due to layout variations (Nature, IEEE, arXiv).Solution: We inverted the dependency.Primary Source: External Metadata APIs (arXiv) via arxiv_metadata.py.Secondary Source: PDF Heuristics (fallback).Enrichment: PDF text is now used primarily for NLP tagging and Search indexing, not for strict metadata authority.B. NLP Normalization Layer (text_normalizer.py)Problem: Raw PDF text contained artifacts (cyber- security, AbstractIntroduction, header junk).Solution: Built a regex-based pre-processor that runs before any NLP task.Re-joins hyphenated words.Inserts missing spaces between case transitions (CamelCase → Camel Case).Removes publisher noise (URLs, "Review Article").C. Permanent Storage StrategyImplemented storage.py to save files as uploads/pdfs/{uuid}.pdf.Replaced temporary file handling with a durable, collision-free UUID system.Enabled Delete functionality that cleans up both the Database record and the physical file, preventing storage leaks.3. New Modules Delivered📊 Analytics Engine (analytics.py)Purpose: Aggregates data for the dashboard.Key Functions:papers_per_year(): Time-series distribution.top_keywords(): Frequency analysis of AI-extracted tags.papers_by_journal(): Source breakdown.📄 Metadata Clients (arxiv_metadata.py)Purpose: Fetches high-quality metadata using arXiv ID detection.Logic: Detect ID in PDF text → Call API → Fill Authors/Year/Title → Fallback to Heuristics.🧹 Text Normalizer (text_normalizer.py)Purpose: Cleans raw PDF garbage before it hits the NLP pipeline.4. Code Highlight: The Metadata-First LogicThis snippet demonstrates the new, robust ingestion flow in 1_Upload_Papers.py:Python# 1. Normalize Raw Text
raw_text = extract_pdf_text(pdf_path)
full_text = normalize_text(raw_text)

# 2. Metadata First Strategy
arxiv_id = extract_arxiv_id(full_text)
if arxiv_id:
    meta = fetch_arxiv_metadata(arxiv_id)  # Authoritative
else:
    meta = {}  # Fallback to heuristics

# 3. Fill Fields with Priority
title = meta.get("title") or extract_pdf_title(pdf_path)
authors = meta.get("authors", [])
year = meta.get("year", 0)

# 4. Content Enrichment (NLP)
abstract = extract_abstract(full_text)
keywords = extract_keywords(abstract)
5. Current System Capabilities (v0.3)FeatureStatusNotesIngestion✅ MatureSupports CSV & PDF with Metadata fallback.Storage✅ ProductionUUID-based permanent storage + clean deletion.NLP✅ AdvancedSmart stopwords, normalization, boundary slicing.Analytics✅ LiveKeyword trends, year distribution, source tracking.Search✅ RobustFilters by Text, Author, Year.Authors⚠️ HybridPerfect for arXiv; fallback heuristics for others.6. Future Roadmap (Phase 4 candidates)Semantic Search: Replace Regex with Vector Embeddings (sentence-transformers).Advanced NLP: Integrate spaCy for Named Entity Recognition (NER) on non-arXiv papers.Citation Graph: Link papers based on references.User Accounts: Multi-user support

Here is the Phase 4 Engineering Log. Save this as PHASE_4_LOG.md in your project folder. This is a critical document because it proves you possess AI Engineering skills, not just web development skills.

📘 MetaScan Phase 4 Engineering Log
Project: MetaScan AI Indexer Version: v0.4 (Semantic Intelligence & Vector Search) Date: December 2025 Status: Phase 4 Complete

1. Executive Summary
Phase 4 elevated MetaScan from a standard keyword-based search engine to an Intelligent Semantic Discovery Platform. We integrated a Vector Embedding Engine using the all-MiniLM-L6-v2 transformer model, enabling the system to understand the conceptual meaning of research papers rather than just matching text strings. This update solves the critical "vocabulary mismatch" problem in research discovery (e.g., searching for "AI" finds papers about "Neural Networks").

2. Technical Architecture: The Vector Pipeline
We implemented a standard Retrieval-Augmented architecture for search:

1. Ingestion Time (The "Write" Path): PDF Text → Sentence Transformer Model → 384-Dimensional Vector → MongoDB Storage

2. Query Time (The "Read" Path): User Query → Generate Query Vector → Cosine Similarity Calculation → Ranked Results

3. Key Modules Delivered
A. Vector Engine (vector_engine.py)
Model Selection: Integrated HuggingFace all-MiniLM-L6-v2.

Reasoning: Chosen for its high speed and low memory footprint (80MB) while maintaining state-of-the-art performance on semantic clustering tasks.

Math Logic: Implemented Cosine Similarity using numpy to calculate the distance between the query vector and document vectors. A score of 1.0 indicates a perfect conceptual match.

B. Hybrid Search Interface
UI Update: Modified the Search Page (2_Search_Papers.py) to support a Hybrid Toggle:

Exact Match Mode: Uses MongoDB $regex for precise filtering (Author, Year).

Semantic Mode: Uses Vector Search for conceptual discovery, featuring a "Similarity Score" indicator (e.g., Match: 0.85).

C. Embedding Storage
Schema Update: Extended the MongoDB papers collection schema to include an embedding field:

Type: Array of 384 floats.

Purpose: persistent storage of "neural" patterns, allowing fast retrieval without re-processing PDFs.

4. Code Highlight: Semantic Similarity Logic
This snippet demonstrates the core mathematical engine driving the semantic search:

Python

def cosine_similarity(vec_a, vec_b):
    """
    Calculates the cosine angle between two non-zero vectors.
    Output: 0.0 (unrelated) to 1.0 (identical meaning).
    """
    if not vec_a or not vec_b:
        return 0.0
    
    a = np.array(vec_a)
    b = np.array(vec_b)
    
    # Dot product / (Magnitude A * Magnitude B)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
5. Challenges & Solutions
Challenge: "Glued Text" Artifacts. Some PDFs (especially LaTeX-generated) lacked space characters, resulting in merged words (e.g., systemdesign).

Impact: Standard Regex keyword search failed completely.

Solution: Vector Embeddings. The transformer model successfully mapped "glued" text to the correct conceptual space, allowing the search to find relevant papers even when the raw text was messy. This proved the resilience of the semantic approach over strict keyword matching.

6. Future Roadmap (Phase 5 Candidates)
Scale: Migrate from local numpy calculation to MongoDB Atlas Vector Search (ANN index) for sub-second retrieval on millions of documents.

RAG (Retrieval-Augmented Generation): Feed the top semantic search results into an LLM to generate natural language answers ("Summarize the findings of these 5 papers").

Graph: Build a citation network to visualize paper influence.

📝 End of Phase 4 Log
Phase 4 successfully transformed MetaScan into an AI-native application, capable of "understanding" research concepts beyond simple keywords.

