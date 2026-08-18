import sys
import os

# Make sure the ResumeATS folder is on the path so its internal imports work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
RESUME_DIR = os.path.join(PROJECT_ROOT, "ResumeATS")

if RESUME_DIR not in sys.path:
    sys.path.insert(0, RESUME_DIR)

# Run inside the ResumeATS folder so relative file paths (.env etc.) resolve correctly
_original_cwd = os.getcwd()
os.chdir(RESUME_DIR)
try:
    with open(os.path.join(RESUME_DIR, "app.py"), encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, os.path.join(RESUME_DIR, "app.py"), "exec"), {"__name__": "__main__", "__file__": os.path.join(RESUME_DIR, "app.py")})
finally:
    os.chdir(_original_cwd)
