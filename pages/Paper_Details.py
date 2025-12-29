import os
import streamlit as st
from metascan.db import get_paper
from metascan.db import delete_paper


st.title("📄 Research Paper Details")

paper_id = st.query_params.get("id", "")

if not paper_id:
    st.error("No paper selected.")
    st.stop()

paper = get_paper(paper_id)

if not paper:
    st.error("Paper not found.")
    st.stop()

st.header(paper.get("title", "Untitled"))

st.write("### 🧑‍🔬 Authors")
st.write(", ".join(paper.get("authors", [])) or "Not available")

st.write("### 📅 Year")
st.write(paper.get("year", "Unknown"))

st.write("### 📘 Journal")
st.write(paper.get("journal", "Unknown"))

st.write("### 📝 Abstract")
st.write(paper.get("abstract", "No abstract available"))

st.write("### 🔑 Keywords")
st.write(", ".join(paper.get("keywords", [])))

st.write("### 🏷 Tags")
st.write(", ".join(paper.get("tags", [])))

st.write("### 📄 PDF")

file_path = paper.get("file_path", "")

if file_path and os.path.exists(file_path):
    with open(file_path, "rb") as f:
        st.download_button(
            label="⬇️ Download PDF",
            data=f,
            file_name=os.path.basename(file_path),
            mime="application/pdf"
        )
else:
    st.warning("PDF file not found on server.")

# ✅ PASTE THIS INSTEAD:

# Optional: Show who uploaded it (Visible to everyone)
if "uploaded_by" in paper:
    st.caption(f"Index uploaded by user: {paper['uploaded_by']}")

st.divider()

# ========================================================
# 🔒 DANGER ZONE (ADMINS ONLY)
# ========================================================
if st.session_state.get("role") == "admin":
    st.subheader("⚠️ Danger Zone (Admin Only)")
    with st.expander("Show Admin Controls"):
        st.warning("This action cannot be undone.")
        
        # Added a unique key='admin_del' just in case
        if st.button("🗑️ Permanently Delete Paper", type="primary", key="admin_del"):
            success = delete_paper(paper_id)

            if success:
                st.success("Paper deleted successfully!")
                st.write("Return to Search...")
                # Redirects automatically
                st.switch_page("pages/2_Search.py")
            else:
                st.error("Failed to delete paper.")


