"""
scorer.py
Core scoring engine: combines keyword (TF-IDF) similarity, semantic
(sentence-embedding) similarity, and skill-overlap into a final ATS match score.
"""
import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from text_processor import clean_text, remove_stopwords_and_lemmatize, extract_skills

# Load the embedding model once (small, fast model — good for a mini project)
_embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def keyword_similarity_score(resume_text, jd_text):
    """TF-IDF + cosine similarity between resume and JD. Returns 0-100."""
    resume_clean = remove_stopwords_and_lemmatize(clean_text(resume_text))
    jd_clean = remove_stopwords_and_lemmatize(clean_text(jd_text))

    if not resume_clean.strip() or not jd_clean.strip():
        return 0.0

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def semantic_similarity_score(resume_text, jd_text):
    """Sentence-embedding cosine similarity — catches meaning-based matches. Returns 0-100."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    embeddings = _embed_model.encode([resume_text, jd_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    # Embedding similarity for unrelated text rarely goes below ~0.2, so rescale
    # a bit for a more intuitive 0-100 spread. Clamp to [0, 1] first.
    score = max(0.0, min(1.0, float(score)))
    return round(score * 100, 2)


def skill_match_analysis(resume_text, jd_text):
    """
    Extract skills from both texts and compute overlap.
    Returns dict with matched, missing, extra skills and a skill match %.
    """
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))

    if not jd_skills:
        return {
            "matched": sorted(resume_skills),
            "missing": [],
            "extra": [],
            "skill_score": 0.0,
        }

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    skill_score = round((len(matched) / len(jd_skills)) * 100, 2)

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "skill_score": skill_score,
    }


def compute_overall_score(keyword_score, semantic_score, skill_score,
                           w_keyword=0.25, w_semantic=0.40, w_skill=0.35):
    """
    Weighted combination of the three sub-scores into one final ATS match %.
    Semantic gets the highest weight since it best reflects true relevance.
    """
    overall = (keyword_score * w_keyword) + (semantic_score * w_semantic) + (skill_score * w_skill)
    return round(overall, 2)


def analyze(resume_text, jd_text):
    """
    Run the full scoring pipeline and return a single results dictionary
    that the UI layer can render directly.
    """
    kw_score = keyword_similarity_score(resume_text, jd_text)
    sem_score = semantic_similarity_score(resume_text, jd_text)
    skills = skill_match_analysis(resume_text, jd_text)
    overall = compute_overall_score(kw_score, sem_score, skills["skill_score"])

    return {
        "overall_score": overall,
        "keyword_score": kw_score,
        "semantic_score": sem_score,
        "skill_score": skills["skill_score"],
        "matched_skills": skills["matched"],
        "missing_skills": skills["missing"],
        "extra_skills": skills["extra"],
    }
