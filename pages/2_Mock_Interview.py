import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
MOCKINTER_DIR = os.path.join(PROJECT_ROOT, "MockInter")

if MOCKINTER_DIR not in sys.path:
    sys.path.insert(0, MOCKINTER_DIR)

_original_cwd = os.getcwd()
os.chdir(MOCKINTER_DIR)
try:
    file_path = os.path.join(MOCKINTER_DIR, "app.py")
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, file_path, "exec"), {"__name__": "__main__", "__file__": file_path})
finally:
    os.chdir(_original_cwd)
