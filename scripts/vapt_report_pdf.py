#!/usr/bin/env python3
"""PDF Report Generator for VAPT Reports.

Generates a professional PDF report from VAPT findings data.
Requires: pip install reportlab
"""

import json
import sys
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
except ImportError:
    print("Error: reportlab is required for PDF generation.")
    print("Install: pip install reportlab")
    sys.exit(1)


# Color scheme
COLORS = {
    "critical": colors.HexColor("#DC2626"),
    "high": colors.HexColor("#EA580C"),
    "medium": colors.HexColor("#CA8A04"),
    "low": colors.HexColor("#2563EB"),
    "info": colors.HexColor("#6B7280"),
    "pass": colors.HexColor("#16A34A"),
    "header_bg": colors.HexColor("#1E293B"),
    "header_text": colors.white,
    "row_alt": colors.HexColor("#F8FAFC"),
}


def severity_color(severity: str) -> colors.Color:
    """Get color for severity level."""
    return COLORS.get(severity.lower(), COLORS["info"])


def build_cover_page(elements: list, styles: dict, data: dict):
    """Build the cover page."""
    elements.append(Spacer(1, 2 * inch))
    elements.append(
        Paragraph("Vulnerability Assessment", styles["CoverTitle"])
    )
    elements.append(Paragraph("& Penetration Test Report", styles["CoverTitle"]))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(data.get("target", "Unknown"), styles["CoverTarget"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(
        Paragraph(data.get("date", datetime.now().strftime("%Y-%m-%d")), styles["CoverDate"])
    )
    elements.append(Spacer(1, 1 * inch))
    elements.append(
        Paragraph("CONFIDENTIAL", styles["Confidential"])
    )
    elements.append(PageBreak())


def build_executive_summary(elements: list, styles: dict, data: dict):
    """Build the executive summary section."""
    elements.append(Paragraph("Executive Summary", styles["SectionTitle"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Score
    score = data.get("overall_score", 0)
    rating = data.get("overall_rating", "Unknown")
    score_color = (
        COLORS["critical"] if score < 30
        else COLORS["high"] if score < 50
        else COLORS["medium"] if score < 70
        else COLORS["pass"] if score < 90
        else COLORS["pass"]
    )

    elements.append(
        Paragraph(
            f'Security Posture Score: <font color="{score_color.hexval()}">'
            f"{score}/100 ({rating})</font>",
            styles["ScoreText"],
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    # Findings summary table
    findings = data.get("findings", [])
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for f in findings:
        sev = f.get("severity", "Info")
        if sev in severity_counts:
            severity_counts[sev] += 1

    summary_data = [["Severity", "Count"]]
    for sev, count in severity_counts.items():
        summary_data.append([sev, str(count)])

    summary_table = Table(summary_data, colWidths=[2 * inch, 1.5 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["header_bg"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["header_text"]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLORS["row_alt"]]),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))

    total = sum(severity_counts.values())
    elements.append(
        Paragraph(f"Total findings: {total}", styles["Normal"])
    )
    elements.append(PageBreak())


def build_findings_section(elements: list, styles: dict, data: dict):
    """Build the detailed findings section."""
    elements.append(Paragraph("Detailed Findings", styles["SectionTitle"]))
    elements.append(Spacer(1, 0.2 * inch))

    findings = data.get("findings", [])
    # Sort by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    findings.sort(key=lambda f: severity_order.get(f.get("severity", "Info"), 5))

    for i, finding in enumerate(findings, 1):
        sev = finding.get("severity", "Info")
        sev_col = severity_color(sev)

        elements.append(
            Paragraph(
                f'<font color="{sev_col.hexval()}">[{sev.upper()}]</font> '
                f'{finding.get("id", f"FINDING-{i:03d}")}: {finding.get("title", "Untitled")}',
                styles["FindingTitle"],
            )
        )
        elements.append(Spacer(1, 0.1 * inch))

        # Finding metadata table
        meta_data = [
            ["CVSS Score", f'{finding.get("cvss_score", "N/A")}'],
            ["CWE", finding.get("cwe", "N/A")],
            ["OWASP", finding.get("owasp", "N/A")],
            ["Affected URL", finding.get("url", "N/A")],
            ["Parameter", finding.get("parameter", "N/A")],
        ]
        meta_table = Table(meta_data, colWidths=[1.5 * inch, 4.5 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(meta_table)
        elements.append(Spacer(1, 0.1 * inch))

        if finding.get("description"):
            elements.append(Paragraph("Description:", styles["SubHeading"]))
            elements.append(Paragraph(finding["description"], styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        if finding.get("impact"):
            elements.append(Paragraph("Impact:", styles["SubHeading"]))
            elements.append(Paragraph(finding["impact"], styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        if finding.get("remediation"):
            elements.append(Paragraph("Remediation:", styles["SubHeading"]))
            elements.append(Paragraph(finding["remediation"], styles["Normal"]))

        elements.append(Spacer(1, 0.3 * inch))


def build_category_scores(elements: list, styles: dict, data: dict):
    """Build category score breakdown."""
    elements.append(Paragraph("Category Breakdown", styles["SectionTitle"]))
    elements.append(Spacer(1, 0.2 * inch))

    categories = data.get("categories", [])
    if not categories:
        elements.append(Paragraph("No category data available.", styles["Normal"]))
        return

    cat_data = [["Category", "Weight", "Score", "Findings"]]
    for cat in categories:
        cat_data.append(
            [
                cat.get("name", ""),
                f'{cat.get("weight", 0)}%',
                f'{cat.get("score", 0)}/100',
                str(sum(cat.get("findings_count", {}).values())),
            ]
        )

    cat_table = Table(cat_data, colWidths=[2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
    cat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["header_bg"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["header_text"]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLORS["row_alt"]]),
            ]
        )
    )
    elements.append(cat_table)
    elements.append(PageBreak())


def generate_pdf(data: dict, output_path: str):
    """Generate the full PDF report."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    # Custom styles
    base_styles = getSampleStyleSheet()
    styles = {
        "Normal": base_styles["Normal"],
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            textColor=COLORS["header_bg"],
        ),
        "CoverTarget": ParagraphStyle(
            "CoverTarget",
            fontSize=18,
            alignment=TA_CENTER,
            fontName="Helvetica",
            textColor=colors.HexColor("#475569"),
        ),
        "CoverDate": ParagraphStyle(
            "CoverDate",
            fontSize=14,
            alignment=TA_CENTER,
            fontName="Helvetica",
            textColor=colors.HexColor("#64748B"),
        ),
        "Confidential": ParagraphStyle(
            "Confidential",
            fontSize=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            textColor=COLORS["critical"],
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            fontSize=18,
            leading=22,
            fontName="Helvetica-Bold",
            textColor=COLORS["header_bg"],
            spaceAfter=6,
        ),
        "ScoreText": ParagraphStyle(
            "ScoreText",
            fontSize=16,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
        "FindingTitle": ParagraphStyle(
            "FindingTitle",
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=COLORS["header_bg"],
        ),
        "SubHeading": ParagraphStyle(
            "SubHeading",
            fontSize=10,
            fontName="Helvetica-Bold",
            spaceAfter=4,
        ),
    }

    elements = []

    build_cover_page(elements, styles, data)
    build_executive_summary(elements, styles, data)
    build_category_scores(elements, styles, data)
    build_findings_section(elements, styles, data)

    doc.build(elements)
    print(f"PDF report generated: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 vapt_report_pdf.py <input.json> [output.pdf]")
        print("  input.json: Report data in JSON format")
        print("  output.pdf: Output path (default: VAPT-REPORT.pdf)")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "VAPT-REPORT.pdf"

    with open(input_path) as f:
        report_data = json.load(f)

    generate_pdf(report_data, output_path)
