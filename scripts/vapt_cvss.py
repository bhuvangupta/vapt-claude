#!/usr/bin/env python3
"""CVSS v3.1 Score Calculator for VAPT Reports."""

import json
import math
import sys

# CVSS v3.1 metric values
METRICS = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20},
    "AC": {"L": 0.77, "H": 0.44},
    "PR": {
        "U": {"N": 0.85, "L": 0.62, "H": 0.27},
        "C": {"N": 0.85, "L": 0.68, "H": 0.50},
    },
    "UI": {"N": 0.85, "R": 0.62},
    "C": {"H": 0.56, "L": 0.22, "N": 0.0},
    "I": {"H": 0.56, "L": 0.22, "N": 0.0},
    "A": {"H": 0.56, "L": 0.22, "N": 0.0},
}


def roundup(x: float) -> float:
    """CVSS roundup function."""
    return math.ceil(x * 10) / 10


def calculate_cvss(vector: str) -> dict:
    """Calculate CVSS v3.1 score from vector string.

    Args:
        vector: CVSS vector string, e.g. "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"

    Returns:
        dict with score, severity, and parsed metrics.
    """
    parts = vector.replace("CVSS:3.1/", "").replace("CVSS:3.0/", "").split("/")
    m = {}
    for part in parts:
        key, val = part.split(":")
        m[key] = val

    scope = m["S"]
    av = METRICS["AV"][m["AV"]]
    ac = METRICS["AC"][m["AC"]]
    pr = METRICS["PR"][scope][m["PR"]]
    ui = METRICS["UI"][m["UI"]]
    c = METRICS["C"][m["C"]]
    i = METRICS["I"][m["I"]]
    a = METRICS["A"][m["A"]]

    # Impact Sub Score
    iss = 1 - ((1 - c) * (1 - i) * (1 - a))

    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)

    # Exploitability
    exploitability = 8.22 * av * ac * pr * ui

    if impact <= 0:
        score = 0.0
    elif scope == "U":
        score = roundup(min(impact + exploitability, 10))
    else:
        score = roundup(min(1.08 * (impact + exploitability), 10))

    # Severity rating
    if score == 0.0:
        severity = "None"
    elif score <= 3.9:
        severity = "Low"
    elif score <= 6.9:
        severity = "Medium"
    elif score <= 8.9:
        severity = "High"
    else:
        severity = "Critical"

    return {
        "vector": vector,
        "score": score,
        "severity": severity,
        "metrics": m,
        "impact_subscore": round(impact, 1),
        "exploitability_subscore": round(exploitability, 1),
    }


def severity_to_penalty(severity: str) -> int:
    """Convert severity to Security Posture Score penalty."""
    penalties = {
        "Critical": 40,
        "High": 25,
        "Medium": 15,
        "Low": 5,
        "None": 0,
    }
    return penalties.get(severity, 0)


def calculate_posture_score(findings: list) -> dict:
    """Calculate Security Posture Score from findings.

    Args:
        findings: List of dicts with 'category' and 'severity' keys.

    Returns:
        dict with overall score, rating, and per-category scores.
    """
    weights = {
        "injection": 0.20,
        "authentication": 0.15,
        "authorization": 0.12,
        "api": 0.12,
        "ssl": 0.10,
        "headers": 0.08,
        "network": 0.08,
        "scan": 0.07,
        "logic": 0.05,
        "recon": 0.03,
    }

    category_penalties = {cat: 0 for cat in weights}

    for finding in findings:
        cat = finding.get("category", "").lower()
        sev = finding.get("severity", "None")
        if cat in category_penalties:
            category_penalties[cat] += severity_to_penalty(sev)

    category_scores = {}
    for cat, weight in weights.items():
        raw = max(0, 100 - category_penalties[cat])
        category_scores[cat] = {
            "score": raw,
            "weight": weight,
            "weighted": round(raw * weight, 1),
        }

    overall = sum(cs["weighted"] for cs in category_scores.values())
    overall = round(min(100, max(0, overall)), 1)

    if overall >= 90:
        rating = "Excellent"
    elif overall >= 70:
        rating = "Good"
    elif overall >= 50:
        rating = "Fair"
    elif overall >= 30:
        rating = "Poor"
    else:
        rating = "Critical"

    return {
        "overall_score": overall,
        "rating": rating,
        "categories": category_scores,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 vapt_cvss.py 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'")
        print("  python3 vapt_cvss.py --posture findings.json")
        sys.exit(1)

    if sys.argv[1] == "--posture":
        with open(sys.argv[2]) as f:
            findings = json.load(f)
        result = calculate_posture_score(findings)
        print(json.dumps(result, indent=2))
    else:
        result = calculate_cvss(sys.argv[1])
        print(json.dumps(result, indent=2))
