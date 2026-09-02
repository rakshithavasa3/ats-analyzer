"""
report_generator.py
Generates a downloadable PDF summary report of the resume analysis using fpdf2.
Kept intentionally simple (no external fonts/images) so it works offline and
requires no extra system dependencies beyond the fpdf2 pip package.
"""

from datetime import datetime
from fpdf import FPDF


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(20, 20, 20)
        self.cell(0, 10, "AI-Powered Resume ATS Analysis Report", ln=True)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, datetime.now().strftime("Generated on %B %d, %Y at %I:%M %p"), ln=True)
        self.ln(4)
        self.set_draw_color(220, 220, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 20, 20)
        self.ln(2)
        self.cell(0, 8, title, ln=True)
        self.set_draw_color(230, 230, 230)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text, size=10):
        self.set_font("Helvetica", "", size)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def label_value(self, label, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(55, 6, label, ln=False)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 20, 20)
        self.cell(0, 6, str(value), ln=True)

    def skill_list(self, label, skills, color):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*color)
        self.cell(0, 6, f"{label} ({len(skills)})", ln=True)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        text = ", ".join(skills) if skills else "None"
        self.multi_cell(0, 5, text)
        self.ln(2)


def _clean_for_pdf(text):
    """
    fpdf2's core Helvetica font only supports latin-1. Replace common Unicode
    punctuation (em-dashes, smart quotes, bullets) with ASCII equivalents first,
    so they render correctly instead of showing up as '?'.
    """
    replacements = {
        "\u2014": "-",   # em-dash
        "\u2013": "-",   # en-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2022": "-",   # bullet
        "\u00a0": " ",   # non-breaking space
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf_report(results, format_warnings, jd_info, readability, insight_paragraphs,
                         output_path="ats_report.pdf"):
    """
    Build the full PDF report and save it to output_path.
    Returns the output_path for convenience.
    """
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # --- Overall score ---
    pdf.section_title("Overall Match Score")
    pdf.set_font("Helvetica", "B", 28)
    overall = results["overall_score"]
    if overall >= 75:
        color = (34, 139, 87)
    elif overall >= 50:
        color = (200, 140, 30)
    else:
        color = (190, 60, 50)
    pdf.set_text_color(*color)
    pdf.cell(0, 14, f"{overall}%", ln=True)
    pdf.ln(2)

    pdf.section_title("Score Breakdown")
    pdf.label_value("Keyword Match:", f"{results['keyword_score']}%")
    pdf.label_value("Semantic Similarity:", f"{results['semantic_score']}%")
    pdf.label_value("Skill Coverage:", f"{results['skill_score']}%")
    pdf.ln(2)

    # --- AI Insights ---
    pdf.section_title("AI Insights")
    for para in insight_paragraphs:
        pdf.body_text(_clean_for_pdf(para))
        pdf.ln(1)

    # --- Skills ---
    pdf.section_title("Skill Gap Analysis")
    pdf.skill_list("Matched Skills", [_clean_for_pdf(s) for s in results["matched_skills"]], (34, 139, 87))
    pdf.skill_list("Missing Skills", [_clean_for_pdf(s) for s in results["missing_skills"]], (190, 60, 50))
    pdf.skill_list("Extra Skills (not required by JD)", [_clean_for_pdf(s) for s in results["extra_skills"]], (100, 100, 100))

    # --- ATS Format Checker ---
    pdf.section_title("ATS Format Compatibility")
    if format_warnings:
        for w in format_warnings:
            pdf.body_text(f"- {_clean_for_pdf(w)}")
    else:
        pdf.body_text("No major formatting issues detected. Resume structure looks ATS-friendly.")
    pdf.ln(1)

    # --- JD Competitiveness ---
    pdf.section_title("JD Competitiveness Indicator")
    pdf.label_value("Seniority Level:", jd_info["seniority"])
    pdf.label_value("Competitiveness:", jd_info["competitiveness_level"])
    pdf.label_value("Required Skills Count:", jd_info["num_required_skills"])
    pdf.body_text(_clean_for_pdf(jd_info["competitiveness_reason"]))
    pdf.ln(1)

    # --- Readability ---
    pdf.section_title("Resume Readability")
    if "flesch_score" in readability:
        pdf.label_value("Flesch Reading Ease Score:", readability["flesch_score"])
        pdf.label_value("Approx. Grade Level:", readability["grade_level"])
        pdf.body_text(_clean_for_pdf(readability["verdict"]))

    pdf.output(output_path)
    return output_path