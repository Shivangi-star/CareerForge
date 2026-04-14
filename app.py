import os
import sys
import re
import pickle
from flask import Flask, render_template, request

# ── Stopwords ────────────────────────────────────────────────
try:
    import nltk
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words('english'))
except Exception:
    STOP_WORDS = {
        'i','me','my','we','our','you','your','he','him','his','she','her',
        'it','its','they','them','their','what','which','who','this','that',
        'these','those','am','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','a','an','the','and','but','if',
        'or','as','of','at','by','for','with','about','into','through','to',
        'from','up','in','out','on','off','then','here','there','when','where',
        'all','both','each','more','most','other','some','no','not','only',
        'same','so','than','too','very','can','will','just','should','now'
    }

# ── Find the folder that contains model.pkl ──────────────────
# Check multiple locations so the app works regardless of how it's launched
def find_base_dir():
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),   # folder of app.py
        os.getcwd(),                                    # current working dir
        os.path.dirname(os.path.abspath(sys.argv[0])), # folder of launched script
    ]
    for d in candidates:
        if os.path.exists(os.path.join(d, 'model.pkl')):
            return d
    # Return app.py folder as fallback (error will show correct path)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = find_base_dir()
print(f"[app] BASE_DIR  : {BASE_DIR}")
print(f"[app] model.pkl : {'FOUND' if os.path.exists(os.path.join(BASE_DIR,'model.pkl')) else 'MISSING'}")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ── Global model state ───────────────────────────────────────
_model       = None
_vectorizer  = None
_model_error = None

def base_ctx(**kw):
    ctx = dict(model_error=None, error=None, verdict=None, verdict_text=None,
               confidence=0, fake_prob=0, real_prob=0, keywords=[],
               original_text=None, highlighted_text=None)
    ctx.update(kw)
    return ctx

def load_models():
    global _model, _vectorizer, _model_error
    if _model is not None:
        return True
    if _model_error is not None:
        return False

    model_path = os.path.join(BASE_DIR, 'model.pkl')
    vec_path   = os.path.join(BASE_DIR, 'vectorizer.pkl')

    missing = [n for p, n in [(model_path,'model.pkl'),(vec_path,'vectorizer.pkl')]
               if not os.path.exists(p)]
    if missing:
        _model_error = (
            f"{', '.join(missing)} not found in: {BASE_DIR}\n"
            "Run:  python train.py   then restart app.py"
        )
        return False
    try:
        with open(model_path, 'rb') as f: _model      = pickle.load(f)
        with open(vec_path,   'rb') as f: _vectorizer = pickle.load(f)
        print("[app] Models loaded successfully.")
        return True
    except Exception as e:
        _model_error = f"Failed to load model files: {e}"
        return False

# ── Text processing ──────────────────────────────────────────
def clean_text(text):
    text  = str(text).lower()
    text  = re.sub(r'http\S+', '', text)
    text  = re.sub(r'[^a-zA-Z]', ' ', text)
    words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 1]
    return ' '.join(words)

def highlight_keywords(original, keywords, verdict):
    css = {'fake':'mark-fake','real':'mark-real','uncertain':'mark-uncertain'}.get(verdict,'mark-uncertain')
    result = original.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    for kw in keywords:
        result = re.compile(r'\b('+re.escape(kw)+r')\b', re.IGNORECASE).sub(
            rf'<mark class="{css}">\1</mark>', result)
    return result

# ── Routes ───────────────────────────────────────────────────
@app.route('/')
def home():
    ok = load_models()
    return render_template('index.html', **base_ctx(model_error=None if ok else _model_error))

@app.route('/predict', methods=['POST'])
def predict():
    if not load_models():
        return render_template('index.html', **base_ctx(model_error=_model_error, error=_model_error))

    input_mode = request.form.get('input_mode', 'text')
    news = ''
    if input_mode == 'file':
        f = request.files.get('news_file')
        if f and f.filename:
            news = f.read().decode('utf-8', errors='ignore')
        else:
            return render_template('index.html', **base_ctx(error='No file uploaded.'))
    else:
        news = request.form.get('news', '').strip()

    if not news.strip():
        return render_template('index.html', **base_ctx(error='Please enter some text.'))

    cleaned = clean_text(news)
    if not cleaned.strip():
        return render_template('index.html', **base_ctx(error='Text has no meaningful words after cleaning.'))

    transformed = _vectorizer.transform([cleaned])
    raw_pred    = _model.predict(transformed)[0]

    if hasattr(_model, 'predict_proba'):
        proba      = _model.predict_proba(transformed)[0]
        classes    = list(_model.classes_)
        real_prob  = round(float(proba[classes.index(0)]) * 100, 1)
        fake_prob  = round(float(proba[classes.index(1)]) * 100, 1)
        confidence = round(float(max(proba)) * 100, 1)
    else:
        confidence = 75.0
        fake_prob, real_prob = (75.0, 25.0) if raw_pred == 1 else (25.0, 75.0)

    keywords = []
    try:
        fn  = _vectorizer.get_feature_names_out()
        coef = _model.coef_[0]
        idx  = transformed.nonzero()[1]
        scores = [(fn[i], coef[i] * transformed[0, i]) for i in idx]
        keywords = [w for w, _ in sorted(scores, key=lambda x: abs(x[1]), reverse=True)[:12]]
    except Exception as e:
        print('Keyword error:', e)

    if   confidence < 60:   verdict, verdict_text = 'uncertain', 'Uncertain — Needs Verification'
    elif raw_pred == 1:      verdict, verdict_text = 'fake',      'Fake News Detected'
    else:                    verdict, verdict_text = 'real',      'Real News'

    return render_template('index.html', **base_ctx(
        verdict=verdict, verdict_text=verdict_text,
        confidence=confidence, fake_prob=fake_prob, real_prob=real_prob,
        keywords=keywords, original_text=news,
        highlighted_text=highlight_keywords(news, keywords, verdict),
    ))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
