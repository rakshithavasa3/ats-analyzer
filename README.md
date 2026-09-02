# AI-Powered Resume ATS Analyzer

A mini project that analyzes how well a resume matches a job description (JD),
combining keyword matching, semantic (AI) similarity, skill-gap analysis, and
two unique features not found in typical ATS tools:

- **ATS Format Compatibility Checker** — flags tables, images, text boxes, and
  multi-column layouts that break real ATS parsers.
- **JD Competitiveness Indicator** — classifies the job's seniority level and
  estimates how competitive/demanding the role is, purely from the JD text.

Runs **fully offline** — no API keys required.

---

## 1. Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the spaCy language model
python -m spacy download en_core_web_sm
```

> Note: the first run will also download the `all-MiniLM-L6-v2` sentence
> embedding model (~90 MB) automatically — this requires an internet
> connection the first time only, after which it's cached locally.

## 2. Run the app

```bash
streamlit run app.py
```

This opens the app in your browser (usually at `http://localhost:8501`).

## 3. How to use

1. Upload a resume (PDF or DOCX).
2. Paste the job description text.
3. Click **Analyze Resume**.
4. Review:
   - Overall ATS match score (gauge)
   - Sub-scores: keyword match, semantic similarity, skill coverage
   - Matched / missing / extra skills
   - ATS format warnings (tables, images, layout issues)
   - JD seniority level + competitiveness
   - Resume readability score

---

## Project structure

```
ats_analyzer/
├── app.py                   # Streamlit UI (main entry point)
├── resume_parser.py         # PDF/DOCX text extraction + ATS format checker
├── text_processor.py        # Text cleaning + skill extraction (spaCy)
├── scorer.py                # TF-IDF, semantic similarity, skill scoring
├── jd_analyzer.py           # JD Competitiveness Indicator
├── readability_checker.py   # Readability scoring (textstat)
├── skills_data.py           # Skills taxonomy + seniority keyword lists
├── requirements.txt
└── README.md
```

## Architecture

```
Resume (PDF/DOCX) ──► Text Extraction ──► Cleaning ──► Skill Extraction
Job Description    ──► Cleaning        ──► Skill Extraction
                                │
                    ┌───────────┼────────────┐
              Keyword Match  Semantic Match  Skill Overlap
                 (TF-IDF)   (Sentence Embed)
                    │           │                  │
                    └─────► Weighted ATS Score ◄────┘
                                │
                    ┌───────────┼────────────────┐
          ATS Format Checker  JD Competitiveness  Readability Check
                                │
                          Streamlit Dashboard
```

## Tech stack

| Component | Library |
|---|---|
| UI | Streamlit |
| PDF parsing | pdfplumber |
| DOCX parsing | python-docx |
| NLP / skill extraction | spaCy |
| Keyword similarity | scikit-learn (TF-IDF + cosine similarity) |
| Semantic similarity | sentence-transformers (`all-MiniLM-L6-v2`) |
| Charts | Plotly |
| Readability | textstat |

## Scoring methodology

The overall ATS match score is a weighted combination of three sub-scores:

```
Overall Score = 0.25 × Keyword Score + 0.40 × Semantic Score + 0.35 × Skill Score
```

- **Keyword Score** — TF-IDF cosine similarity between cleaned resume and JD text.
- **Semantic Score** — sentence-embedding cosine similarity; catches meaning-based
  matches even when exact wording differs (e.g. "led a team" ≈ "team leadership").
- **Skill Score** — percentage of JD-required skills also found in the resume,
  based on a curated skills taxonomy (`skills_data.py`).

Weights can be tuned in `scorer.py` → `compute_overall_score()`.

## Known limitations / future scope

- Scanned/image-based PDFs are not OCR'd (text extraction will fail or be empty).
- Skill taxonomy is a fixed list — extend `skills_data.py` for niche domains.
- No LLM-based personalized suggestions (kept rule-based for offline use);
  could be added later with an OpenAI/Gemini API key.
- No downloadable PDF report yet (planned future feature).
- No resume version-tracking / before-after comparison (planned future feature).
