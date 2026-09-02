"""
readability_checker.py
Bonus feature: resume readability scoring using textstat.
Purely offline — no API or Java dependency (unlike grammar-check libraries
such as language_tool_python, which need a Java runtime + downloads).
"""

import textstat


def check_readability(resume_text):
    """Return readability metrics + a simple human-friendly verdict."""
    if not resume_text.strip():
        return {"score": 0, "verdict": "No text to analyze.", "details": {}}

    flesch_score = textstat.flesch_reading_ease(resume_text)
    grade_level = textstat.text_standard(resume_text, float_output=False)

    if flesch_score >= 60:
        verdict = "Easy to read — clear and ATS/recruiter friendly."
    elif flesch_score >= 30:
        verdict = "Moderately readable — consider shortening some sentences."
    else:
        verdict = "Hard to read — sentences may be too long/complex. Simplify wording."

    return {
        "flesch_score": round(flesch_score, 2),
        "grade_level": grade_level,
        "verdict": verdict,
    }
