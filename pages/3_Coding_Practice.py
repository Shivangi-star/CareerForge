import sys
import os
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
CODING_DIR = os.path.join(PROJECT_ROOT, "CodingPract")

if CODING_DIR not in sys.path:
    sys.path.insert(0, CODING_DIR)

st.sidebar.markdown("### Coding Practice View")
mode = st.sidebar.radio(
    "Choose view:",
    ["Practice Questions", "Submission Dashboard"],
    key="coding_mode_select"
)

target_file = "DSA_app_db.py" if mode == "Practice Questions" else "DSA_dash.py"

_original_cwd = os.getcwd()
os.chdir(CODING_DIR)
try:
    file_path = os.path.join(CODING_DIR, target_file)
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, file_path, "exec"), {"__name__": "__main__", "__file__": file_path})
finally:
    os.chdir(_original_cwd)
