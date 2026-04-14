"""
train.py — Fake News Detection Model Trainer
Run this ONCE before starting app.py:
    python train.py

Requires Fake.csv and True.csv in the same folder.
Download from: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset
"""

import os, sys, re, pickle, warnings
warnings.filterwarnings('ignore')

print("=" * 55)
print("  Fake News Detection — Model Trainer")
print("=" * 55)

# ── 1. Check CSV files exist ─────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
fake_path = os.path.join(BASE_DIR, 'Fake.csv')
true_path = os.path.join(BASE_DIR, 'True.csv')

for p, name in [(fake_path, 'Fake.csv'), (true_path, 'True.csv')]:
    if not os.path.exists(p):
        print(f"\n  ERROR: {name} not found in {BASE_DIR}")
        print("  Download both files from:")
        print("  https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset")
        print("  and place them in the same folder as train.py\n")
        sys.exit(1)

# ── 2. Import libraries ──────────────────────────────────────
print("\n[1/6] Importing libraries...")
try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report
except ImportError as e:
    print(f"\n  ERROR: Missing library — {e}")
    print("  Run:  pip install pandas scikit-learn numpy")
    sys.exit(1)

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

# ── 3. Load data ─────────────────────────────────────────────
print("[2/6] Loading data...")
fake = pd.read_csv(fake_path)
true = pd.read_csv(true_path)

fake['label'] = 1
true['label'] = 0

df = pd.concat([fake, true], axis=0).reset_index(drop=True)
print(f"      Fake articles : {len(fake)}")
print(f"      Real articles : {len(true)}")
print(f"      Total         : {len(df)}")

# ── 4. Clean text ────────────────────────────────────────────
print("[3/6] Cleaning text (this may take a minute)...")

def clean_text(text):
    text  = str(text).lower()
    text  = re.sub(r'http\S+', '', text)
    text  = re.sub(r'[^a-zA-Z]', ' ', text)
    words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 1]
    return ' '.join(words)

df['content']    = df['title'].fillna('') + ' ' + df['text'].fillna('')
df['clean_text'] = df['content'].apply(clean_text)
df = df[df['clean_text'].str.strip() != ''].reset_index(drop=True)
print(f"      Rows after cleaning: {len(df)}")

# ── 5. Vectorise & train ─────────────────────────────────────
print("[4/6] Vectorising with TF-IDF...")
X = df['clean_text']
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer  = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)
print(f"      Train shape: {X_train_vec.shape}")

print("[5/6] Training Logistic Regression...")
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_vec, y_train)

# ── 6. Evaluate ──────────────────────────────────────────────
y_pred = model.predict(X_test_vec)
acc    = accuracy_score(y_test, y_pred)
print(f"\n      ✓ Accuracy : {acc*100:.2f}%")
print()
print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))

# ── 7. Save ──────────────────────────────────────────────────
print("[6/6] Saving model.pkl and vectorizer.pkl...")
with open(os.path.join(BASE_DIR, 'model.pkl'), 'wb') as f:
    pickle.dump(model, f)
with open(os.path.join(BASE_DIR, 'vectorizer.pkl'), 'wb') as f:
    pickle.dump(vectorizer, f)

print()
print("=" * 55)
print("  Training complete!")
print("  model.pkl and vectorizer.pkl saved.")
print()
print("  Now run:  python app.py")
print("  Then open: http://127.0.0.1:5000")
print("=" * 55)
