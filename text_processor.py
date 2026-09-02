"""
text_processor.py
Text cleaning and skill extraction using spaCy's PhraseMatcher.
"""

import re
import spacy
from spacy.matcher import PhraseMatcher
from skills_data import ALL_SKILLS

# Load spaCy model once (small English model — fast and good enough for this task)
_nlp = spacy.load("en_core_web_sm")

# Build a PhraseMatcher for skill extraction (case-insensitive, multi-word aware)
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
_skill_patterns = [_nlp.make_doc(skill) for skill in ALL_SKILLS]
_matcher.add("SKILLS", _skill_patterns)


def clean_text(text):
    """Lowercase, strip extra whitespace/punctuation noise, keep words meaningful for matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\s/-]", " ", text)  # keep +, #, . for things like c++, c#, node.js
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text):
    """
    Extract known skills from text using PhraseMatcher.
    Returns a sorted set of skill strings found in the text.
    """
    doc = _nlp(text.lower())
    matches = _matcher(doc)
    found = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        found.add(span.text.strip())
    return sorted(found)


def remove_stopwords_and_lemmatize(text):
    """Return a cleaned, lemmatized, stopword-free version of text (used for TF-IDF)."""
    doc = _nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) > 1
    ]
    return " ".join(tokens)
