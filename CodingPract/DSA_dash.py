import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

SQLITE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coding_prep.db")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Coding Submissions Dashboard")
st.caption("Track problem solving progress and acceptance rates.")

with st.sidebar:
    user_id = st.text_input("Candidate ID / Username:", value="candidate1")

if os.path.exists(SQLITE_DB):
    conn = sqlite3.connect(SQLITE_DB)
    df = pd.read_sql_query("SELECT * FROM submissions WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
else:
    df = pd.DataFrame()

if df.empty:
    st.info(f"No coding submissions found for user '{user_id}'. Solve problems in 'Practice Questions' to populate stats!")
else:
    m1, m2, m3 = st.columns(3)
    total_sub = len(df)
    accepted_sub = len(df[df['status'] == 'Accepted'])
    acc_rate = round((accepted_sub / total_sub * 100), 1) if total_sub > 0 else 0

    with m1:
        st.metric("Total Submissions", f"{total_sub}")
    with m2:
        st.metric("Accepted Submissions", f"{accepted_sub}")
    with m3:
        st.metric("Acceptance Rate", f"{acc_rate}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Submission Status Breakdown")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig1 = px.pie(status_counts, names='Status', values='Count', template="plotly_dark", hole=0.4)
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Submissions by Category")
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig2 = px.bar(cat_counts, x='Category', y='Count', template="plotly_dark", color='Category')
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📜 Recent Submission History")
    st.dataframe(df[['problem_title', 'difficulty', 'category', 'status', 'timestamp']], use_container_width=True)
