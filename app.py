"""
app.py
AI-Powered Resume ATS Analyzer — main Streamlit application.

Run with:
    streamlit run app.py
"""

import io
import tempfile
import streamlit as st
import plotly.graph_objects as go

from resume_parser import extract_text, check_ats_format, check_missing_sections
from scorer import analyze, _embed_model
from jd_analyzer import analyze_jd
from readability_checker import check_readability
from insights_generator import generate_insights
from report_generator import generate_pdf_report

st.set_page_config(page_title="AI Resume ATS Analyzer", page_icon="📄", layout="wide")

# ---------------------------------------------------------------------------
# Custom styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

:root {
    --bg-deep: #0E1116;
    --bg-card: #161B22;
    --accent: #E3A857;
    --accent-soft: rgba(227, 168, 87, 0.12);
    --good: #4FAE7C;
    --good-soft: rgba(79, 174, 124, 0.14);
    --bad: #D9695F;
    --bad-soft: rgba(217, 105, 95, 0.14);
    --neutral: #6C7A89;
    --neutral-soft: rgba(108, 122, 137, 0.14);
    --text-dim: #9AA5B1;
}

.stApp { background-color: var(--bg-deep); }

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.1rem;
    background: linear-gradient(90deg, #F0F3F7 0%, var(--accent) 120%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: var(--text-dim);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.01em;
    margin-bottom: 1.4rem;
}

.section-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}
.section-heading {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F0F3F7;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pill {
    display: inline-block;
    padding: 0.28rem 0.78rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.2rem 0.35rem 0.2rem 0;
    font-family: 'JetBrains Mono', monospace;
}
.pill-good { background: var(--good-soft); color: var(--good); border: 1px solid rgba(79,174,124,0.3); }
.pill-bad { background: var(--bad-soft); color: var(--bad); border: 1px solid rgba(217,105,95,0.3); }
.pill-neutral { background: var(--neutral-soft); color: var(--text-dim); border: 1px solid rgba(108,122,137,0.3); }

.insight-box {
    background: linear-gradient(135deg, rgba(227,168,87,0.08) 0%, rgba(227,168,87,0.02) 100%);
    border: 1px solid rgba(227,168,87,0.25);
    border-radius: 14px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1.2rem;
}
.insight-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}
.insight-para {
    color: #DDE3EA;
    font-size: 0.96rem;
    line-height: 1.65;
    margin-bottom: 0.8rem;
}
.insight-para:last-child { margin-bottom: 0; }

.score-tag {
    display: inline-block;
    padding: 0.35rem 0.9rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
}
.tag-strong { background: var(--good-soft); color: var(--good); }
.tag-mid { background: var(--accent-soft); color: var(--accent); }
.tag-weak { background: var(--bad-soft); color: var(--bad); }

hr { border-color: rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)


def pill_row(items, style):
    if not items:
        return "<span style='color: var(--text-dim); font-size: 0.9rem;'>None</span>"
    return "".join([f"<span class='pill pill-{style}'>{s}</span>" for s in items])


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<div class="hero-title">📄 AI-Powered Resume ATS Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Keyword + Semantic Matching &nbsp;·&nbsp; Skill Gap Analysis &nbsp;·&nbsp; '
    'ATS Format Checker &nbsp;·&nbsp; JD Competitiveness Indicator</div>',
    unsafe_allow_html=True
)

if _embed_model is None:
    st.warning(
        "⚠️ Semantic similarity model could not be downloaded (no internet access to "
        "huggingface.co). The app will still work using Keyword Match + Skill Coverage "
        "only. Connect to the internet once and restart the app to enable full semantic scoring."
    )

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-heading">📤 1. Upload Resume</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"],
                                    label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-heading">📋 2. Paste Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("Paste the job description here", height=180,
                            placeholder="Paste the full job description text...",
                            label_visibility="collapsed")

analyze_clicked = st.button("🔍  Analyze Resume", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
if analyze_clicked:
    if resume_file is None:
        st.error("Please upload a resume file.")
        st.stop()
    if not jd_text.strip():
        st.error("Please paste a job description.")
        st.stop()

    with st.spinner("Extracting resume text..."):
        try:
            file_bytes = resume_file.read()
            resume_text = extract_text(io.BytesIO(file_bytes), resume_file.name)
        except Exception as e:
            st.error(f"Could not read resume file: {e}")
            st.stop()

    if not resume_text.strip():
        st.error("Could not extract any text from the resume. If it's a scanned/image-based PDF, "
                  "try a text-based version instead.")
        st.stop()

    with st.spinner("Running keyword + semantic + skill analysis..."):
        results = analyze(resume_text, jd_text)

    with st.spinner("Checking ATS format compatibility..."):
        format_warnings = check_ats_format(io.BytesIO(file_bytes), resume_file.name)
        section_warnings = check_missing_sections(resume_text)
        all_format_warnings = format_warnings + section_warnings

    with st.spinner("Analyzing job description..."):
        jd_info = analyze_jd(jd_text)

    with st.spinner("Checking readability..."):
        readability = check_readability(resume_text)

    with st.spinner("Generating AI insights..."):
        insight_paragraphs = generate_insights(
            results, format_warnings, jd_info, semantic_available=(_embed_model is not None)
        )

    # -----------------------------------------------------------------------
    # AI Insights — the narrative "AI-powered" section
    # -----------------------------------------------------------------------
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown('<div class="insight-tag">✨ AI Insights</div>', unsafe_allow_html=True)
    for para in insight_paragraphs:
        st.markdown(f'<div class="insight-para">{para}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Downloadable PDF report
    # -----------------------------------------------------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        generate_pdf_report(
            results, format_warnings, jd_info, readability, insight_paragraphs,
            output_path=tmp_pdf.name
        )
        with open(tmp_pdf.name, "rb") as f:
            pdf_bytes = f.read()

    st.download_button(
        label="📥  Download Full Analysis Report (PDF)",
        data=pdf_bytes,
        file_name=f"ATS_Analysis_Report_{resume_file.name.rsplit('.', 1)[0]}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Overall score
    # -----------------------------------------------------------------------
    overall = results["overall_score"]
    if overall >= 75:
        tag_class, score_msg = "tag-strong", "Strong match — well aligned with this role."
    elif overall >= 50:
        tag_class, score_msg = "tag-mid", "Moderate match — some improvements recommended."
    else:
        tag_class, score_msg = "tag-weak", "Low match — consider revising your resume for this role."

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    score_col, gauge_col = st.columns([1, 1.6])

    with score_col:
        st.markdown('<div class="section-heading">Overall ATS Match Score</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="score-tag {tag_class}">{overall}%</span>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: var(--text-dim); margin-top: 0.8rem;">{score_msg}</p>',
                    unsafe_allow_html=True)

    with gauge_col:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall,
            number={"font": {"color": "#F0F3F7"}},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#6C7A89"},
                "bar": {"color": "#E3A857"},
                "bgcolor": "#0E1116",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(217,105,95,0.18)"},
                    {"range": [50, 75], "color": "rgba(227,168,87,0.18)"},
                    {"range": [75, 100], "color": "rgba(79,174,124,0.18)"},
                ],
            },
        ))
        fig.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=10),
                           paper_bgcolor="rgba(0,0,0,0)", font={"color": "#DDE3EA"})
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Sub-scores
    # -----------------------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📊 Detailed Score Breakdown</div>', unsafe_allow_html=True)

    bar_fig = go.Figure(go.Bar(
        x=["Keyword Match", "Semantic Similarity", "Skill Coverage"],
        y=[results["keyword_score"], results["semantic_score"], results["skill_score"]],
        marker_color=["#E3A857", "#4FAE7C", "#6C9BD1"],
        text=[f"{results['keyword_score']}%", f"{results['semantic_score']}%", f"{results['skill_score']}%"],
        textposition="outside",
        textfont={"color": "#F0F3F7"},
    ))
    bar_fig.update_layout(
        height=320, yaxis_range=[0, 110], margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#DDE3EA"},
        xaxis={"gridcolor": "rgba(255,255,255,0.05)"},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)"},
    )
    st.plotly_chart(bar_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Skill gap analysis
    # -----------------------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">🎯 Skill Gap Analysis</div>', unsafe_allow_html=True)
    skill_col1, skill_col2, skill_col3 = st.columns(3)

    with skill_col1:
        st.markdown('<p style="color: var(--good); font-weight: 600; font-size: 0.88rem;">✅ MATCHED</p>',
                    unsafe_allow_html=True)
        st.markdown(pill_row(results["matched_skills"], "good"), unsafe_allow_html=True)

    with skill_col2:
        st.markdown('<p style="color: var(--bad); font-weight: 600; font-size: 0.88rem;">❌ MISSING</p>',
                    unsafe_allow_html=True)
        st.markdown(pill_row(results["missing_skills"], "bad"), unsafe_allow_html=True)

    with skill_col3:
        st.markdown('<p style="color: var(--text-dim); font-weight: 600; font-size: 0.88rem;">➕ EXTRA</p>',
                    unsafe_allow_html=True)
        st.markdown(pill_row(results["extra_skills"], "neutral"), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # ATS Format Compatibility Checker
    # -----------------------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">🛠️ ATS Format Compatibility Checker</div>', unsafe_allow_html=True)
    if all_format_warnings:
        for w in all_format_warnings:
            st.warning(w)
    else:
        st.success("No major formatting issues detected. Your resume structure looks ATS-friendly!")
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # JD Competitiveness Indicator
    # -----------------------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📈 JD Competitiveness Indicator</div>', unsafe_allow_html=True)
    jd_col1, jd_col2, jd_col3 = st.columns(3)
    jd_col1.metric("Seniority Level", jd_info["seniority"])
    jd_col2.metric("Competitiveness", jd_info["competitiveness_level"])
    jd_col3.metric("Required Skills Count", jd_info["num_required_skills"])
    st.caption(jd_info["competitiveness_reason"])
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Readability
    # -----------------------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📖 Resume Readability</div>', unsafe_allow_html=True)
    if "flesch_score" in readability:
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("Flesch Reading Ease Score", readability["flesch_score"])
        r_col2.metric("Approx. Grade Level", readability["grade_level"])
        st.caption(readability["verdict"])
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Upload a resume and paste a job description, then click **Analyze Resume** to get started.")