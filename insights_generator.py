"""
insights_generator.py
Generates a natural-language "AI Insights" narrative summarizing the resume
analysis — the kind of write-up a human career coach (or a real LLM) would give.
Fully rule-based and offline: no API key needed, but reads like genuine AI output
because it reasons over the actual computed scores/skills instead of templating
generic text.
"""

import random


def _opening_line(overall_score, seniority):
    if overall_score >= 75:
        options = [
            f"Strong alignment here — your resume is well-positioned for this {seniority.lower()} role.",
            f"This is a strong match. Your background lines up closely with what this {seniority.lower()} role needs.",
        ]
    elif overall_score >= 50:
        options = [
            f"You're in the right neighborhood for this {seniority.lower()} role, but a few gaps are holding your score back.",
            f"Decent overlap with this {seniority.lower()} posting — some targeted edits could meaningfully lift your score.",
        ]
    else:
        options = [
            f"There's a real gap between your resume and this {seniority.lower()} posting right now.",
            f"This {seniority.lower()} role wants a different emphasis than what your resume currently highlights.",
        ]
    return random.choice(options)


def _skill_paragraph(matched_skills, missing_skills, extra_skills):
    parts = []

    if matched_skills:
        shown = matched_skills[:5]
        parts.append(
            f"You already show up well on {len(matched_skills)} of the skills this role wants"
            + (f" — including {', '.join(shown)}" if shown else "") + "."
        )

    if missing_skills:
        shown = missing_skills[:5]
        more = f" and {len(missing_skills) - 5} more" if len(missing_skills) > 5 else ""
        parts.append(
            f"The clearest opportunity is closing the gap on {', '.join(shown)}{more} — "
            "if you have hands-on experience with these, make sure the exact terms appear "
            "on your resume, since ATS systems match literally, not just conceptually."
        )
    else:
        parts.append("Notably, there are no missing required skills — a strong sign for this role.")

    if extra_skills and len(extra_skills) >= 3:
        parts.append(
            f"You also list {len(extra_skills)} skills this JD doesn't ask for — not a problem, "
            "but consider trimming ones irrelevant to this specific application to keep the resume focused."
        )

    return " ".join(parts)


def _format_paragraph(format_warnings):
    if not format_warnings:
        return "Your resume's structure looks clean and ATS-friendly — no formatting red flags detected."
    lead = "Before you submit, address a structural risk: " if len(format_warnings) == 1 else \
           "Before you submit, address a few structural risks: "
    return lead + " ".join(format_warnings)


def _score_breakdown_paragraph(keyword_score, semantic_score, skill_score, semantic_available):
    if not semantic_available:
        return (
            f"Your keyword overlap sits at {keyword_score}% and skill coverage at {skill_score}%. "
            "(Semantic similarity wasn't available this run — connect to the internet and restart "
            "for the full AI-based meaning analysis.)"
        )

    weakest = min([("keyword match", keyword_score), ("semantic relevance", semantic_score),
                    ("skill coverage", skill_score)], key=lambda x: x[1])
    return (
        f"Breaking it down: keyword overlap is {keyword_score}%, semantic relevance "
        f"(how closely the meaning of your experience matches the role, beyond exact words) "
        f"is {semantic_score}%, and skill coverage is {skill_score}%. "
        f"Your biggest lever right now is {weakest[0]} — that's the sub-score with the most room to grow."
    )


def generate_insights(results, format_warnings, jd_info, semantic_available=True):
    """
    Build a multi-paragraph natural-language insight summary from all the
    computed analysis results. Returns a list of paragraph strings.
    """
    overall = results["overall_score"]
    seniority = jd_info.get("seniority", "this")

    paragraphs = [
        _opening_line(overall, seniority),
        _score_breakdown_paragraph(
            results["keyword_score"], results["semantic_score"], results["skill_score"], semantic_available
        ),
        _skill_paragraph(results["matched_skills"], results["missing_skills"], results["extra_skills"]),
        _format_paragraph(format_warnings),
    ]

    return paragraphs