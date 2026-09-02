"""
resume_parser.py
Extracts raw text from PDF/DOCX resumes and inspects layout/structure
(used later by the ATS Format Compatibility Checker).
"""

import pdfplumber
import docx


def extract_text_from_pdf(file_path_or_buffer):
    """Extract all text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path_or_buffer) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_path_or_buffer):
    """Extract all text from a DOCX file."""
    document = docx.Document(file_path_or_buffer)
    text = "\n".join([para.text for para in document.paragraphs if para.text.strip()])
    return text.strip()


def extract_text(file_path_or_buffer, filename):
    """
    Dispatch to the correct extractor based on file extension.
    `filename` is used only to detect the extension (works for uploaded
    Streamlit file objects which don't have a real file path).
    """
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_path_or_buffer)
    elif ext in ("docx",):
        return extract_text_from_docx(file_path_or_buffer)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Please upload a PDF or DOCX file.")


# ---------------------------------------------------------------------------
# ATS Format Compatibility Checker
# ---------------------------------------------------------------------------
def check_pdf_format(file_path_or_buffer):
    """
    Inspect a PDF's layout for elements that commonly break ATS parsers:
    tables, images, and multi-column layouts.
    Returns a list of warning strings (empty list = looks clean).
    """
    warnings = []
    try:
        with pdfplumber.open(file_path_or_buffer) as pdf:
            has_tables = False
            has_images = False
            multi_column_pages = 0

            for page in pdf.pages:
                if page.extract_tables():
                    has_tables = True
                if page.images:
                    has_images = True

                # crude multi-column heuristic: look at word x-positions
                words = page.extract_words()
                if words:
                    mid_x = page.width / 2
                    left = sum(1 for w in words if w["x0"] < mid_x - 20)
                    right = sum(1 for w in words if w["x0"] > mid_x + 20)
                    if left > 5 and right > 5:
                        multi_column_pages += 1

            if has_tables:
                warnings.append(
                    "Contains tables — many ATS systems fail to parse tabular content correctly."
                )
            if has_images:
                warnings.append(
                    "Contains images/icons — text inside images is invisible to most ATS parsers."
                )
            if multi_column_pages > 0:
                warnings.append(
                    "Appears to use a multi-column layout — ATS often reads columns out of order, "
                    "scrambling the text."
                )
    except Exception:
        warnings.append("Could not fully analyze PDF layout — file may be scanned/image-based.")

    return warnings


def check_docx_format(file_path_or_buffer):
    """
    Inspect a DOCX's structure for elements that commonly break ATS parsers:
    tables, embedded images, and text boxes.
    Returns a list of warning strings.
    """
    warnings = []
    try:
        document = docx.Document(file_path_or_buffer)

        if len(document.tables) > 0:
            warnings.append(
                "Contains tables — many ATS systems fail to parse tabular content correctly."
            )

        # Detect embedded images via inline shapes
        if len(document.inline_shapes) > 0:
            warnings.append(
                "Contains images/icons — text inside images is invisible to most ATS parsers."
            )

        # Detect text boxes (stored differently in the XML, not as normal paragraphs)
        xml_str = document.element.xml
        if "<w:txbxContent" in xml_str:
            warnings.append(
                "Contains text boxes — content inside text boxes is often skipped entirely by ATS."
            )

        # Check for headers/footers with contact info (often invisible to ATS)
        for section in document.sections:
            header_text = section.header.paragraphs[0].text if section.header.paragraphs else ""
            if header_text.strip():
                warnings.append(
                    "Contact info may be placed in the header — some ATS systems ignore header/footer text."
                )
                break

    except Exception:
        warnings.append("Could not fully analyze DOCX structure.")

    return warnings


def check_ats_format(file_path_or_buffer, filename):
    """Dispatch format-compatibility check based on file type."""
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return check_pdf_format(file_path_or_buffer)
    elif ext == "docx":
        return check_docx_format(file_path_or_buffer)
    return []


def check_missing_sections(resume_text):
    """
    Basic check for standard resume sections. Missing sections are flagged
    as they often signal an unusual/non-standard resume structure.
    """
    text_lower = resume_text.lower()
    warnings = []

    section_keywords = {
        "contact info (email)": ["@"],
        "education section": ["education", "b.tech", "bachelor", "degree", "university", "college"],
        "experience/projects section": ["experience", "project", "internship", "work history"],
        "skills section": ["skills", "technical skills", "proficiencies"],
    }

    for section_name, keywords in section_keywords.items():
        if not any(kw in text_lower for kw in keywords):
            warnings.append(f"Could not detect a clear '{section_name}' — consider adding an explicit heading.")

    return warnings
