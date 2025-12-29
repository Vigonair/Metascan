import streamlit as st
from metascan.db import get_all_papers, verify_user, create_user

st.set_page_config(
    page_title="MetaScan Portal",
    page_icon="🔎",
    layout="wide"
)

# --- AUTHENTICATION STATE ---
if "role" not in st.session_state:
    st.session_state["role"] = None
    st.session_state["username"] = None

def login_success(role, username):
    st.session_state["role"] = role
    st.session_state["username"] = username
    st.rerun()

def logout():
    st.session_state["role"] = None
    st.session_state["username"] = None
    st.rerun()

# --- MAIN LOGIC ---

if st.session_state["role"]:
    # ============================================================
    # 🟢 LOGGED IN VIEW (Your Original Dashboard goes here!)
    # ============================================================
    
    # Sidebar Profile
    with st.sidebar:
        st.write(f"👤 **{st.session_state['username']}** ({st.session_state['role'].title()})")
        if st.button("Log Out"):
            logout()
    
    # 1. Dashboard Header
    if st.session_state["role"] == "admin":
        st.title("👑 Admin Dashboard")
        st.success(f"Welcome back, Administrator.")
    else:
        st.title("🔎 MetaScan — Researcher Portal")
        st.success(f"Welcome back, {st.session_state['username']}.")

    # 2. Your Metrics (From your old code)
    papers = get_all_papers()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Papers Indexed", len(papers))
    with c2:
        st.metric("Your Access Level", st.session_state["role"].upper())
    
    st.write("---")
    
    # 3. Navigation Guide
    st.subheader("Navigate your tools:")
    if st.session_state["role"] == "admin":
        st.markdown("""
        - **📤 Upload & Manage:** Add new papers or delete existing ones.
        - **👮 Admin Panel:** Review user uploads.
        - **📊 Analytics:** View system statistics.
        """)
    else:
        st.markdown("""
        - **🔍 Search:** Find papers using keywords or AI concepts.
        - **📤 Contribute:** Upload papers (Admin will review).
        """)

else:
    # ============================================================
    # 🔴 LOGIN / REGISTER VIEW (The Gatekeeper)
    # ============================================================
    st.title("🔐 MetaScan Access")
    st.write("Please log in to access the research index.")
    
    st.write("") # Spacer
    
    # 1. Choose Identity
    user_type = st.radio("Who are you?", ["👤 User (Researcher)", "👑 Admin"], horizontal=True)
    
    st.divider()

    if user_type == "👑 Admin":
        # ADMIN LOGIN
        with st.form("admin_login"):
            st.write("### Admin Access")
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Admin Panel")
            
            if submitted:
                if user == "admin" and pwd == "admin123":
                    login_success("admin", "admin")
                else:
                    st.error("Invalid Admin Credentials")

    else:
        # USER FLOW
        tab1, tab2 = st.tabs(["Log In", "Register New Account"])
        
        with tab1:
            with st.form("user_login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In")
                
                if submitted:
                    user_data = verify_user(username, password)
                    if user_data:
                        login_success("user", user_data["username"])
                    else:
                        st.error("User not found or wrong password.")
        
        with tab2:
            with st.form("user_register"):
                new_user = st.text_input("Choose Username")
                new_pwd = st.text_input("Choose Password", type="password")
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if new_user and new_pwd:
                        if create_user(new_user, new_pwd):
                            st.success("Account created! Go to the 'Log In' tab.")
                        else:
                            st.error("Username already taken.")
                    else:
                        st.warning("Please fill in all fields.")
