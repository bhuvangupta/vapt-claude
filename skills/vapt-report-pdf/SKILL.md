# PDF Report Generation

## When Invoked

The user runs `/vapt report-pdf <url>`.

## Prerequisites

- Python 3.8+
- `reportlab` package installed (`pip install reportlab`)
- VAPT output files in the current directory (ideally run `/vapt report` first)

## Behavior

Generate a professional PDF report from VAPT findings using the `scripts/vapt_report_pdf.py` script.

## Phase 1: Data Collection

Same as `vapt-report` -- scan for all VAPT output files, parse findings, calculate scores.

## Phase 2: PDF Generation

### 2.1 Compile Report Data

Assemble a JSON structure with all report data:

```json
{
    "target": "example.com",
    "date": "2026-03-19",
    "tester": "...",
    "authorization": "Pentest engagement",
    "overall_score": 42,
    "overall_rating": "Poor",
    "categories": [
        {"name": "Injection", "weight": 20, "score": 15, "findings_count": {"critical": 2, "high": 1}},
        ...
    ],
    "findings": [
        {
            "id": "FINDING-001",
            "title": "SQL Injection in /api/users",
            "severity": "Critical",
            "cvss_score": 9.8,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
            "cwe": "CWE-89",
            "owasp": "A03:2021",
            "url": "/api/users?id=1",
            "parameter": "id",
            "description": "...",
            "steps": ["..."],
            "impact": "...",
            "remediation": "..."
        },
        ...
    ],
    "scope": {"in_scope": [...], "out_of_scope": [...]},
    "tools_used": [...]
}
```

### 2.2 Run PDF Script

```bash
python3 <skills_dir>/scripts/vapt_report_pdf.py --input report_data.json --output VAPT-REPORT.pdf
```

### 2.3 PDF Structure

The PDF report includes:

**Cover Page:**
- "Vulnerability Assessment & Penetration Test Report"
- Target URL
- Date
- Authorization reference
- Confidentiality notice

**Table of Contents:**
- Auto-generated with page numbers

**Executive Summary (Page 1-2):**
- Security Posture Score gauge (visual, color-coded)
- Finding count by severity (bar chart)
- Category score breakdown (radar chart or table)
- Top 3 risks highlighted
- Key recommendations

**Findings Detail (Page 3+):**
- One finding per section
- Color-coded severity badge
- CVSS score with visual indicator
- Full details: description, steps, evidence, impact, remediation

**Category Breakdown:**
- Score per category with visual bar
- Finding count per category

**Remediation Priority Matrix:**
- Color-coded priority table
- Timeline recommendations

**Methodology & Scope:**
- Testing approach
- Tools used
- Scope boundaries

**Appendix:**
- CVSS reference
- Glossary

### 2.4 Visual Design

**Color scheme:**
- Critical: #DC2626 (red)
- High: #EA580C (orange)
- Medium: #CA8A04 (yellow)
- Low: #2563EB (blue)
- Info: #6B7280 (gray)
- Pass/Good: #16A34A (green)

**Score gauge:**
- Circular gauge showing 0-100 score
- Color changes based on rating band
- Rating text below gauge

**Charts:**
- Severity distribution bar chart
- Category scores horizontal bar chart

## Phase 3: Output

### Terminal Output

```
Generating PDF report...
  Collected findings from 8 scan files
  Calculated Security Posture Score: 42/100 (Poor)
  Generated 23-page PDF report

Output: VAPT-REPORT.pdf
```

### VAPT-REPORT.pdf

Professional PDF saved to the current directory.

## Error Handling

If `reportlab` is not installed:
```
PDF generation requires the reportlab Python package.
Install: pip install reportlab

Alternatively, generate a Markdown report: /vapt report <url>
```
