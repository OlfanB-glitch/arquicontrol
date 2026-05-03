from pathlib import Path
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate
from reportlab.pdfbase.pdfmetrics import stringWidth


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "16_documento_final_arquicontrol.md"
OUTPUT_PATH = ROOT / "ArquiControl_documento_final.pdf"


def normalize_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.replace("  ", "<br/>")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=HexColor("#111827"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
    )
    styles.add(
        ParagraphStyle(
            name="CoverBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            textColor=HexColor("#374151"),
            spaceAfter=8,
        ),
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=HexColor("#111827"),
            spaceBefore=12,
            spaceAfter=10,
        ),
    )
    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=HexColor("#1f2937"),
            spaceBefore=10,
            spaceAfter=6,
        ),
    )
    styles.add(
        ParagraphStyle(
            name="BodyAcademic",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=HexColor("#1f2937"),
            spaceAfter=8,
        ),
    )
    styles.add(
        ParagraphStyle(
            name="BulletAcademic",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=HexColor("#1f2937"),
            leftIndent=16,
            firstLineIndent=-10,
            spaceAfter=4,
        ),
    )
    return styles


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(HexColor("#d1d5db"))
    canvas.line(doc.leftMargin, 1.6 * cm, A4[0] - doc.rightMargin, 1.6 * cm)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(HexColor("#6b7280"))
    canvas.drawString(doc.leftMargin, 1.0 * cm, "ArquiControl — Documento final académico")
    page_label = f"Página {doc.page}"
    width = stringWidth(page_label, "Helvetica", 9)
    canvas.drawString(A4[0] - doc.rightMargin - width, 1.0 * cm, page_label)
    canvas.restoreState()


def parse_markdown(lines, styles):
    story = []
    paragraph_buffer = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        text = " ".join(part.strip() for part in paragraph_buffer if part.strip())
        if text:
            story.append(Paragraph(normalize_inline(text), styles["BodyAcademic"]))
        paragraph_buffer = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(normalize_inline(stripped[2:]), styles["CoverTitle"]))
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            title = stripped[3:]
            if title == "3. Introducción":
                story.append(PageBreak())
            story.append(Paragraph(normalize_inline(title), styles["SectionTitle"]))
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            title = stripped[4:]
            if title == "2. Tabla de contenido":
                story.append(PageBreak())
            story.append(Paragraph(normalize_inline(title), styles["SubsectionTitle"]))
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            story.append(Paragraph(f"• {normalize_inline(stripped[2:])}", styles["BulletAcademic"]))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            story.append(Paragraph(normalize_inline(stripped), styles["BulletAcademic"]))
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()
    return story


def build_pdf():
    styles = build_styles()
    lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines()
    story = parse_markdown(lines, styles)

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
        title="ArquiControl - Documento final académico",
        author="[[NOMBRE DEL ESTUDIANTE]]",
        subject="Memoria técnica y académica del proyecto ArquiControl",
    )
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


if __name__ == "__main__":
    build_pdf()
    print(f"PDF generado en: {OUTPUT_PATH}")