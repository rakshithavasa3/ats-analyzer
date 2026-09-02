"""
jd_analyzer.py
JD Competitiveness Indicator — a unique feature that classifies a job
description's seniority level and estimates how competitive/demanding it is,
purely with rule-based keyword logic (no external API needed).
"""

from skills_data import SENIOR_INDICATORS, MID_INDICATORS, ENTRY_INDICATORS
from text_processor import extract_skills


def classify_seniority(jd_text):
    """Guess seniority level (Entry / Mid / Senior) based on keyword cues in the JD."""
    text_lower = jd_text.lower()

    senior_hits = sum(1 for kw in SENIOR_INDICATORS if kw in text_lower)
    mid_hits = sum(1 for kw in MID_INDICATORS if kw in text_lower)
    entry_hits = sum(1 for kw in ENTRY_INDICATORS if kw in text_lower)

    if senior_hits > mid_hits and senior_hits > entry_hits:
        return "Senior"
    elif mid_hits >= senior_hits and mid_hits > entry_hits:
        return "Mid-Level"
    elif entry_hits > 0:
        return "Entry-Level"
    else:
        return "Not specified / General"


def estimate_competitiveness(jd_text):
    """
    Rough competitiveness estimate based on number of required skills mentioned
    and JD length (longer, skill-dense JDs usually mean more competitive roles).
    Returns a label + a short explanation.
    """
    skills_found = extract_skills(jd_text)
    num_skills = len(skills_found)
    word_count = len(jd_text.split())

    if num_skills >= 12 or word_count > 400:
        level = "High"
        reason = f"JD lists {num_skills} distinct skills and is fairly detailed ({word_count} words) — expect strong competition."
    elif num_skills >= 6:
        level = "Medium"
        reason = f"JD lists {num_skills} distinct skills — a moderately competitive role."
    else:
        level = "Low"
        reason = f"JD lists only {num_skills} distinct skills — likely broad requirements, less niche competition."

    return {"level": level, "reason": reason, "num_skills": num_skills, "word_count": word_count}


def analyze_jd(jd_text):
    """Full JD analysis: seniority + competitiveness in one call."""
    seniority = classify_seniority(jd_text)
    competitiveness = estimate_competitiveness(jd_text)
    return {
        "seniority": seniority,
        "competitiveness_level": competitiveness["level"],
        "competitiveness_reason": competitiveness["reason"],
        "num_required_skills": competitiveness["num_skills"],
        "jd_word_count": competitiveness["word_count"],
    }
