import spacy
from transformers import pipeline
import subprocess
import sys
import re


def clean_text(text):
    if not text: return ""
    
    # 1. Remove header junk (e.g., "Page 1", "arXiv:...")
    # This removes lines that look like page numbers or headers
    text = re.sub(r"Page \d+|arXiv:\S+", " ", text, flags=re.IGNORECASE)

    # 2. FIX HYPHENATION (The Important Fix 🔧)
    # Catches "cyberse- curity" (space) AND "cyberse-\ncurity" (newline)
    # Looks for: (lowercase letter) + (-) + (whitespace) + (lowercase letter)
    text = re.sub(r"([a-z])-\s+([a-z])", r"\1\2", text)

    # 3. Collapse multiple spaces/newlines into one space
    text = re.sub(r"\s+", " ", text).strip()
    
    # 4. Fix "BiomedicalResearch" -> "Biomedical Research" (CamelCase issues)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    return text
# 1. SETUP SPACY
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# 2. SETUP AI (Lazy Loading)
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("⏳ Loading AI Model... (One-time delay)")
        _classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
    return _classifier

# 3. FAST DICTIONARY (The "Speed Layer")
CATEGORY_RULES = {
    "AI / ML": ["neural", "learning", "gpt", "transformer", "cnn", "model", "ai", "algorithm"],
    "Biomedical": ["patient", "clinical", "disease", "health", "cancer", "biomedical", "inbre", "protein", "gene"],
    "Computer Vision": ["image", "detection", "video", "pixel", "segmentation", "object"],
    "Cybersecurity": ["security", "malware", "attack", "encryption", "network", "phishing"],
    "Physics": ["quantum", "energy", "laser", "particle", "magnetic", "material", "gravitational", "astro"]
}

# 4. SLOW AI LABELS (The "Brain Layer")
CANDIDATE_LABELS = [
    "Artificial Intelligence",
    "Biomedical & Medicine",
    "Astrophysics & Space",
    "Computer Vision",
    "Cybersecurity",
    "Quantum Physics",
    "Economics & Social Science",
    "Environmental Science"
]

def assign_category(text):
    """
    Hybrid Approach:
    1. Try Dictionary (Fast)
    2. If fails, try AI (Smart)
    """
    if not text: return "General"
    
    # --- STEP 1: Fast Dictionary Check ---
    text_lower = text.lower()
    scores = {cat: 0 for cat in CATEGORY_RULES}
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1
    
    best_rule = max(scores, key=scores.get)
    # If we found at least 2 keywords, trust the dictionary (It's fast!)
    if scores[best_rule] >= 2:
        return best_rule

    # --- STEP 2: AI Fallback (Slower but Smarter) ---
    # Only runs if dictionary failed or was unsure
    try:
        classifier = get_classifier()
        # Truncate text to 1024 chars to speed up AI
        result = classifier(text[:1024], CANDIDATE_LABELS)
        
        top_category = result['labels'][0]
        confidence = result['scores'][0]
        
        if confidence > 0.3:
            return top_category
    except Exception as e:
        print(f"AI Warning: {e}")
        pass

    return "General"

# Helper for other files
def extract_keywords_tfidf(text, top_n=5):
    from sklearn.feature_extraction.text import TfidfVectorizer
    if not text: return []
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=top_n)
        vectorizer.fit_transform([text])
        return list(vectorizer.get_feature_names_out())
    except: return []