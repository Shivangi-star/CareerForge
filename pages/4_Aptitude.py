import sys
import os
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
APTITUDE_DIR = os.path.join(PROJECT_ROOT, "Aptitude")

if APTITUDE_DIR not in sys.path:
    sys.path.insert(0, APTITUDE_DIR)

st.sidebar.markdown("### Aptitude View")
mode = st.sidebar.radio(
    "Choose view:",
    ["Take Test", "Performance Dashboard"],
    key="aptitude_mode_select"
)

target_file = "AptiApp.py" if mode == "Take Test" else "InteractiveDashboard.py"

_original_cwd = os.getcwd()
os.chdir(APTITUDE_DIR)
try:
    file_path = os.path.join(APTITUDE_DIR, target_file)
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, file_path, "exec"), {"__name__": "__main__", "__file__": file_path})
finally:
    os.chdir(_original_cwd)
