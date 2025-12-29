# Metascan: AI-Powered Research Engine

Metascan is a full-stack research paper management platform designed to bridge the gap between simple keyword search and semantic understanding. It allows researchers to upload PDF documents, automatically extracts metadata, and performs "Hybrid Search"—combining exact keyword matching with vector-based conceptual search.

## The Mission

Traditional search engines fail when you don't know the exact keyword. If you search for "AI," you might miss a relevant paper titled "Neural Networks" because the keyword doesn't match. Metascan solves this by using local AI models to convert research papers into mathematical vectors, allowing the system to understand that "AI" and "Neural Networks" are semantically related.

## Key Features

* **Hybrid Search Engine:** Simultaneously queries MongoDB for exact matches (Author, Year) and performs Vector Search for conceptual matches (Abstract similarity).
* **Automated Ingestion:** Upload a PDF, and the system automatically extracts text, generates an AI embedding, and indexes it in real-time.
* **Role-Based Access Control (RBAC):** A secure authentication system with distinct privileges for "Researchers" (Upload/Search) and "Admins" (Delete/Moderate).
* **Data Analytics:** Built-in dashboard to visualize publication timelines and category distributions.

## The Engineering Journey: Challenges & Solutions

Building Metascan was not just about connecting APIs; it required solving significant architectural and compatibility challenges.

### Phase 1: The Logic Conflict (Vector vs. Keyword)
**The Challenge:**
The core feature of the app is Hybrid Search. However, the vector search engine returned results as a list of tuples (Document, Score), while the keyword search engine returned a list of Dictionaries. Trying to merge these two disparate data structures caused the application to crash with data unpacking errors.

**The Solution:**
I engineered a standardization layer that intercepts results from both engines. It normalizes them into a consistent JSON-compatible format before they reach the frontend. This ensures that the UI can render results agnostic of the source, whether they came from the AI model or a database query.

### Phase 2: The "Python 3.13" Compatibility Crisis
**The Challenge:**
During the integration of the Hugging Face `transformers` library, the application failed to initialize the AI pipeline due to deep incompatibilities with the latest Python 3.13 environment. The standard library imports were failing, threatening to halt the AI features entirely.

**The Solution:**
Instead of downgrading the entire tech stack to an older Python version (which would sacrifice performance), I debugged the dependency chain. I reconfigured the environment to use specific, stable versions of `torch` and `transformers` that were patched for modern Python runtimes, preserving the performance benefits of the latest interpreter.

### Phase 3: Security & "God Mode"
**The Challenge:**
Implementing an Admin system introduced a major security risk. In early testing, the "Delete Paper" controls were rendered on the client-side for all users. A standard user could accidentally see the "Danger Zone" and delete the entire database.

**The Solution:**
I implemented strict server-side session checks. The frontend now checks the user's encrypted session role before rendering sensitive components. If the role is not explicitly "admin", the destructive functions are never sent to the browser, making it impossible for unauthorized users to trigger them via UI manipulation.

## Tech Stack

* **Frontend:** Streamlit (Python)
* **Database:** MongoDB (Atlas Vector Search)
* **AI Model:** Hugging Face Transformers (all-MiniLM-L6-v2)
* **Authentication:** Custom Session State Management
* **Visualization:** Altair & Pandas

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/Vigonair/Metascan.git](https://github.com/Vigonair/Metascan.git)