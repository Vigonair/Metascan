import streamlit as st
from metascan.search import search_advanced
from metascan.semantic_search import semantic_search,search_similar_papers


st.title("🔍 Search Research Papers")

# -----------------------------
# Search Mode Toggle
# -----------------------------
search_mode = st.radio(
    "Search Mode",
    ["🔍 Exact Match", "🧠 Semantic (AI)"],
    horizontal=True
)

st.write("")

# -----------------------------
# Shared Query Input
# -----------------------------
query = st.text_input(
    "Search",
    placeholder=(
        "Search by title, abstract, keywords"
        if search_mode == "🔍 Exact Match"
        else "Search by concept or research idea"
    )
)

# -----------------------------
# Exact Match Filters
# -----------------------------
author_filter = ""
year_filter = ""

if search_mode == "🔍 Exact Match":
    author_filter = st.text_input("Filter by author (optional)")
    year_filter = st.text_input("Filter by year (optional)")

# -----------------------------
# Semantic Options
# -----------------------------
top_k = 5
if search_mode == "🧠 Semantic (AI)":
    top_k = st.slider("Number of results", 3, 10, 5)

# -----------------------------
# Search Action
# -----------------------------
if st.button("Search"):
    if search_mode == "🔍 Exact Match":
        results = search_advanced(
            query=query,
            author=author_filter,
            year=year_filter
        )

        st.write(f"Found {len(results)} results")

        for r in results:
            st.subheader(r.get("title", "Untitled"))
            st.write("Authors:", ", ".join(r.get("authors", [])) or "Not available")
            st.write("Year:", r.get("year", "N/A"))
            st.write("Journal:", r.get("journal", "N/A"))

            details_url = f"/Paper_Details?id={str(r['_id'])}"
            st.markdown(f"[📄 View Details]({details_url})")
            st.write("---")

    else:
        results = semantic_search(query, top_k=top_k)

        st.write(f"Found {len(results)} semantically similar papers")

        for score, r in results:
            st.subheader(r.get("title", "Untitled"))
            st.write(f"🧠 Similarity Score: {score:.3f}")
            st.write("Year:", r.get("year", "N/A"))
            st.write("Journal:", r.get("journal", "N/A"))

            if r.get("abstract"):
                st.write(r["abstract"][:500] + ("..." if len(r["abstract"]) > 500 else ""))

            details_url = f"/Paper_Details?id={str(r['_id'])}"
            st.markdown(f"[📄 View Details]({details_url})")
            st.write("---")


       
