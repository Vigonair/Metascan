import streamlit as st
import pandas as pd
import plotly.express as px
from metascan.db import get_all_papers



# ==========================================
# 🔒 SECURITY CHECK: ADMINS ONLY
# ==========================================
if "role" not in st.session_state or st.session_state["role"] != "admin":
    st.error("⛔ ACCESS DENIED")
    st.warning("You do not have permission to view this page.")
    st.stop()  # 🛑 This halts the code immediately!
# ==========================================

# ... Your Analytics code starts here ...
st.title("📊 System Analytics")
# etc...
st.set_page_config(page_title="Library Analytics", layout="wide")
st.title("📊 Research Library Analytics")

# 1. Fetch Data
papers = get_all_papers()
if not papers:
    st.info("No data yet. Upload papers first!")
    st.stop()

df = pd.DataFrame(papers)

# Ensure 'category' column exists (fill with 'Uncategorized' if missing)
if "category" not in df.columns:
    df["category"] = "Uncategorized"
df["category"] = df["category"].fillna("Uncategorized")

# ---------------------------------------------------------
# 2. METRICS ROW
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Papers", len(df))
col2.metric("Unique Authors", len(set([a for sublist in df['authors'] for a in sublist])))
if "year" in df.columns:
    # Filter out weird years (like 0)
    valid_years = df[df["year"] > 0]["year"]
    if not valid_years.empty:
        col3.metric("Time Span", f"{int(valid_years.min())} - {int(valid_years.max())}")

st.divider()

# ---------------------------------------------------------
# 3. CHARTS ROW (Pie Chart + Bar Chart)
# ---------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📚 Topics Distribution")
    # Group by category
    cat_counts = df['category'].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    
    # Pie Chart
    fig_pie = px.pie(cat_counts, values="Count", names="Category", hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("📅 Publication Timeline")
    if "year" in df.columns:
        year_counts = df['year'].value_counts().reset_index()
        year_counts.columns = ["Year", "Count"]
        # Filter valid years
        year_counts = year_counts[year_counts["Year"] > 0].sort_values("Year")
        
        # Bar Chart
        fig_bar = px.bar(year_counts, x="Year", y="Count", color="Count")
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# 4. KEYWORDS (Horizontal Bar)
# ---------------------------------------------------------
st.subheader("🏷 Top Keywords")
all_keywords = []
if "keywords" in df.columns:
    for row in df["keywords"]:
        if isinstance(row, list):
            all_keywords.extend(row)

if all_keywords:
    kw_counts = pd.Series(all_keywords).value_counts().head(10).sort_values(ascending=True)
    kw_df = kw_counts.reset_index()
    kw_df.columns = ["Keyword", "Count"]
    
    fig_kw = px.bar(kw_df, x="Count", y="Keyword", orientation='h', title="Most Common Concepts")
    st.plotly_chart(fig_kw, use_container_width=True)
else:
    st.info("No keyword data available.")

st.divider()

# ---------------------------------------------------------
# 5. DRILL DOWN: List Papers by Topic
# ---------------------------------------------------------
st.subheader("🔎 Inspect Papers by Topic")

# Get list of unique categories
categories = ["All"] + sorted(df["category"].unique().tolist())

# Dropdown to select topic
selected_cat = st.selectbox("Select a Category to view papers:", categories)

# Filter the DataFrame based on selection
if selected_cat == "All":
    filtered_df = df
else:
    filtered_df = df[df["category"] == selected_cat]

# Show the table
st.dataframe(
    filtered_df[["title", "year", "authors", "category"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "title": st.column_config.TextColumn("Title", width="medium"),
        "year": st.column_config.NumberColumn("Year", format="%d"),
        "category": st.column_config.TextColumn("Category", width="small"),
    }
)