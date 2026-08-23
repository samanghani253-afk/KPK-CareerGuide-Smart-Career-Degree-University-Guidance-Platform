"""Generates downloadable PDF reports (MASTER PROMPT sections 20-21) using
ReportLab. Falls back gracefully with a clear error if ReportLab isn't
installed rather than crashing the app."""
import io
from datetime import datetime


def _build_story(profile, recommendations, uni_matches, lang_label, parent_friendly=False):
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=12)
    h2 = ParagraphStyle("H2Custom", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]
    small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, textColor=colors.grey)

    story = []
    title = "My Career & University Guidance Report" if not parent_friendly else "Parent-Friendly Career Guidance Summary"
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", small))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Student Profile", h2))
    profile_rows = [
        ["Name", profile.get("name") or "Not provided"],
        ["District/City", f"{profile.get('district','-')}, {profile.get('city','-')}"],
        ["FSc Group", profile.get("fsc_group", "-")],
        ["FSc Percentage", str(profile.get("fsc_percentage") or profile.get("expected_fsc_percentage") or "Not provided")],
        ["Budget Band", profile.get("budget_band", "-")],
        ["Preferred Location", profile.get("preferred_location", "-")],
    ]
    t = Table(profile_rows, colWidths=[150, 320])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Top Recommended Careers", h2))
    for i, rec in enumerate(recommendations, start=1):
        career = rec["career"]
        story.append(Paragraph(f"#{i} {career['name']} — Match Score: {rec['match_score']}/100", styles["Heading3"]))
        if not parent_friendly:
            breakdown_text = ", ".join(f"{k}: {v}/{rec['max_breakdown'][k]}" for k, v in rec["breakdown"].items())
            story.append(Paragraph(f"Why this score? {breakdown_text}", small))
        story.append(Paragraph(f"Entry test: {career.get('entry_test','Needs Verification')}", body))
        story.append(Paragraph(f"Degree duration: {career.get('degree_duration','Needs Verification')}", body))
        story.append(Paragraph(f"Estimated cost band (unverified estimate): {career.get('typical_annual_cost_band','Needs Verification')}", body))
        story.append(Paragraph(f"Career paths: {', '.join(career.get('career_paths', []))}", body))
        story.append(Spacer(1, 8))

    if uni_matches:
        story.append(Paragraph("Best Matching Universities", h2))
        for m in uni_matches[:5]:
            uni = m["university"]
            story.append(Paragraph(f"{uni['name']} — Match: {m['match_score']}%", styles["Heading3"]))
            story.append(Paragraph(f"Type: {uni.get('type','-')} | Location: {uni.get('city','-')} | Verification status: {uni.get('verification_status','Needs verification')}", small))
            story.append(Spacer(1, 6))

    story.append(Paragraph("Important Notice", h2))
    disclaimer = ("This report provides educational career guidance based on the information you provided. "
                  "It is not a guarantee of admission, employment or future income. University eligibility, "
                  "merit, fees, deadlines and entry-test requirements can change — always verify final admission "
                  "information through each university's official sources before making decisions or payments.")
    story.append(Paragraph(disclaimer, small))

    return story


def generate_pdf_report(profile, recommendations, uni_matches=None, lang_label="English", parent_friendly=False) -> bytes:
    """Returns PDF bytes. Raises ImportError if reportlab is unavailable —
    callers should catch this and show a friendly Streamlit message."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40)
    story = _build_story(profile, recommendations, uni_matches, lang_label, parent_friendly)
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
