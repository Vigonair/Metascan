import streamlit as st
from metascan.db import get_all_papers, delete_paper

st.set_page_config(page_title="Admin Panel", layout="wide")

# 🔒 SECURITY CHECK (Double Lock)
if "role" not in st.session_state or st.session_state["role"] != "admin":
    st.error("⛔ ACCESS DENIED")
    st.stop()

st.title("👮 Admin Moderation Panel")

# 1. Fetch all papers
papers = get_all_papers()
st.info(f"Currently managing {len(papers)} papers.")

st.divider()

# 2. Loop through papers and show WHO uploaded them
for p in papers:
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 1])
        
        with c1:
            st.subheader(p.get("title", "Untitled"))
            st.caption(f"ID: {p['_id']}")
            
        with c2:
            # 👇 THIS IS THE PART YOU WANTED
            uploader = p.get("uploaded_by", "Unknown (Admin?)")
            st.write(f"👤 **Uploaded by:** `{uploader}`")
            st.write(f"🏷️ Category: {p.get('category', 'General')}")
            
        with c3:
            # The Delete Button
            if st.button("🗑️ Delete", key=f"del_{p['_id']}"):
                delete_paper(p['_id'])
                st.rerun()