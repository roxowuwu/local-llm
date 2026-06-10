from difflib import get_close_matches


# Known correct words
KNOWN_WORDS = [
    "youtube", "google", "gmail",
    "play", "search", "open",
    "chrome", "firefox"
]


def correct_word(word: str):
    matches = get_close_matches(word, KNOWN_WORDS, n=1, cutoff=0.7)
    return matches[0] if matches else word


def correct_text(text: str) -> str:
    words = text.lower().strip().split()

    corrected = [correct_word(w) for w in words]

    return " ".join(corrected)

