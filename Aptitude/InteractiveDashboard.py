import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_system.db")

def is_mongodb_available():
    if not PYMONGO_AVAILABLE:
        return False
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        return True
    except Exception:
        return False

USE_MONGODB = is_mongodb_available()

def get_test_data(username, category):
    if USE_MONGODB:
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client['quiz_system']
            collection = db['apti_test']
            tests = list(collection.find({"student_id": username, "category": category}))
            if tests:
                df = pd.DataFrame(tests)
                if 'accuracy' not in df.columns and 'marks_achieved' in df.columns:
                    df['accuracy'] = (df['marks_achieved'] / df['no_of_questions']) * 100
                return df
        except Exception:
            pass

    # SQLite fallback
    if os.path.exists(SQLITE_DB_PATH):
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            query = "SELECT * FROM apti_test WHERE student_id = ? AND category = ?"
            df = pd.read_sql_query(query, conn, params=(username, category))
            conn.close()
            if not df.empty:
                if 'accuracy' not in df.columns and 'marks_achieved' in df.columns:
                    df['accuracy'] = (df['marks_achieved'] / df['no_of_questions']) * 100
                return df
        except Exception:
            pass

    return pd.DataFrame()


def assign_performance_category(row):
    acc = row.get('accuracy', 0)
    if acc < 50:
        return "Needs Practice"
    elif acc < 70:
        return "Average"
    elif acc < 90:
        return "Good"
    else:
        return "Excellent"


def improvement_tips(df):
    if df.empty or 'accuracy' not in df.columns:
        return "Take your first test session to unlock personalized performance recommendations."

    avg_accuracy = df['accuracy'].mean()
    tips = []

    if avg_accuracy < 50:
        tips.append("🎯 **Foundation Alert**: Your overall accuracy is below 50%. Focus on foundational formula revisions and topic-by-topic drills.")
    elif avg_accuracy < 70:
        tips.append("📈 **Steady Progress**: You have a moderate score (50-70%). Target weak sub-topics to boost your baseline.")
    elif avg_accuracy < 90:
        tips.append("⭐ **Strong Standing**: High accuracy (70-90%). Focus on speed optimization and time per question.")
    else:
        tips.append("🏆 **Top Tier**: Excellent performance (>90%)! Maintain consistency under full mock exam constraints.")

    if 'time_taken' in df.columns and len(df) > 1:
        avg_time = df['time_taken'].mean()
        tips.append(f"⏱️ **Average Speed**: You average **{avg_time:.1f} seconds** per completed test section.")

    return "\n\n".join(tips)


# --- Streamlit UI Setup ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f3f4f6;
    }
    .metric-box {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Candidate Performance Dashboard")
st.caption("Track test accuracy trends, completion times, and targeted skill improvements.")

with st.sidebar:
    st.header("🔍 Candidate Filter")
    username = st.text_input("Enter Candidate ID / Username:", value="student1")
    category = st.radio("Select Category:", options=["General", "Technical"])
    submit_button = st.button("Generate Dashboard Analytics")

if submit_button or username:
    df = get_test_data(username, category)
    if df.empty:
        st.warning(f"No test records found for '{username}' under category '{category}'. Take a test in the 'Take Test' tab first!")
    else:
        st.markdown("### 📈 Session Summary")
        m1, m2, m3, m4 = st.columns(4)

        total_tests = len(df)
        avg_acc = df['accuracy'].mean() if 'accuracy' in df.columns else 0
        max_score = df['marks_achieved'].max() if 'marks_achieved' in df.columns else 0
        avg_time = df['time_taken'].mean() if 'time_taken' in df.columns else 0

        with m1:
            st.metric("Total Tests Taken", f"{total_tests}")
        with m2:
            st.metric("Average Accuracy", f"{avg_acc:.1f}%")
        with m3:
            st.metric("Highest Score", f"{max_score}")
        with m4:
            st.metric("Avg Time / Test", f"{avg_time:.1f}s")

        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Accuracy Trend")
            if 'test_no' in df.columns:
                fig_line = px.line(
                    df, x='test_no', y='accuracy', markers=True,
                    title='Accuracy (%) across Sessions',
                    labels={'test_no': 'Test Session #', 'accuracy': 'Accuracy (%)'},
                    template="plotly_dark"
                )
                fig_line.update_traces(line_color="#6366f1", marker_size=8)
                fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_line, use_container_width=True)

        with col_chart2:
            st.subheader("Performance Breakdown")
            if 'accuracy' in df.columns:
                df['performance_category'] = df.apply(assign_performance_category, axis=1)
                breakdown = df['performance_category'].value_counts().reset_index()
                breakdown.columns = ['Performance', 'Count']
                fig_pie = px.pie(
                    breakdown, names='Performance', values='Count',
                    title='Grade Distribution', hole=0.4,
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### 💡 AI Recommendations")
        st.info(improvement_tips(df))

        with st.expander("📋 Detailed Test Log Data"):
            st.dataframe(df, use_container_width=True)
