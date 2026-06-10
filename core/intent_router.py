import re
from typing import Tuple

# ML imports (will work only if installed later)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    import joblib
except:
    TfidfVectorizer = None
    LogisticRegression = None


class IntentRouter:

    def __init__(self, prefs=None, model_path="core/intent_model.pkl"):
        self.prefs = prefs
        self.model = None
        self.vectorizer = None

        # Try loading ML model
        try:
            data = joblib.load(model_path)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
        except:
            pass

        # keyword map
        self.keywords = {
            "media": ["play", "song", "music", "video"],
            "app": ["open", "launch", "start"],
            "system": ["shutdown", "restart", "storage"],
            "web": ["search", "google", "youtube"],
            "file": ["create file", "delete file", "read file"]
        }

    # -----------------------------
    # MAIN CLASSIFIER
    # -----------------------------
    def classify(self, user_input: str) -> dict:
        text = user_input.lower().strip()

        # Step 1: keyword scoring
        category, score = self._keyword_score(text)

        confidence = score

        # Step 2: ML fallback
        if score < 0.6 and self.model:
            ml_category, ml_conf = self._ml_classify(text)
            category = ml_category
            confidence = ml_conf

        # Step 3: decision
        needs_llm = False
        if confidence < 0.75 or category == "complex":
            needs_llm = True

        return {
            "category": category,
            "action_hint": category,
            "params": self._extract_params(text),
            "confidence": round(confidence, 2),
            "needs_llm": needs_llm
        }

    # -----------------------------
    # KEYWORD SCORING
    # -----------------------------
    def _keyword_score(self, text) -> Tuple[str, float]:
        scores = {}

        for category, words in self.keywords.items():
            count = sum(1 for w in words if w in text)
            scores[category] = count

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # normalize score
        confidence = min(1.0, max_score / 2)

        if max_score == 0:
            return "complex", 0.0

        return best_category, confidence

    # -----------------------------
    # ML CLASSIFIER
    # -----------------------------
    def _ml_classify(self, text) -> Tuple[str, float]:
        if not self.model or not self.vectorizer:
            return "complex", 0.0

        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]

        idx = probs.argmax()
        category = self.model.classes_[idx]
        confidence = probs[idx]

        return category, float(confidence)

    # -----------------------------
    # PARAM EXTRACTION (simple)
    # -----------------------------
    def _extract_params(self, text):
        params = {}

        # play <something>
        match = re.search(r"play (.+)", text)
        if match:
            params["query"] = match.group(1)

        # open <app>
        match = re.search(r"open (.+)", text)
        if match:
            params["app"] = match.group(1)

        return params
