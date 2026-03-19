# Markdown Report Generation

## When Invoked

The user runs `/vapt report <url>`.

## Behavior

Scan the current directory for all VAPT output files and compile them into a comprehensive, client-ready Markdown report.

## Phase 1: Data Collection

### 1.1 Scan for Output Files

Check for the existence of each output file:

```
VAPT-RECON.md, VAPT-NETWORK.md, VAPT-SSL.md, VAPT-SCAN.md,
VAPT-INJECT.md, VAPT-AUTH.md, VAPT-AUTHZ.md, VAPT-API.md,
VAPT-GRAPHQL.md, VAPT-WEBSOCKET.md, VAPT-CLOUD.md,
VAPT-HEADERS.md, VAPT-LOGIC.md, VAPT-AUDIT.md,
VAPT-WAVE1-CONTEXT.md, VAPT-WAVE2-CONTEXT.md, VAPT-WAVE3-FINDINGS.md,
AUTHORIZATION-LOG.md
```

### 1.2 Parse Findings

From each file, extract:
- All findings with severity, CVSS, CWE
- Steps to reproduce
- Evidence (request/response)
- Remediation recommendations

### 1.3 Handle Partial Data

If some files are missing:
- Note which categories were not tested
- Calculate partial Security Posture Score (only for tested categories)
- Include "Scope and Limitations" section listing untested areas

## Phase 2: Score Calculation

### 2.1 Per-Category Scores

For each testing category with data, calculate:
```
category_score = 100 - sum(severity_penalties)
  Critical: -40, High: -25, Medium: -15, Low: -5, Info: -0
  Floor: 0
```

### 2.2 Overall Security Posture Score

```
overall = sum(category_score * weight) for tested categories
Normalize if not all categories were tested.
```

## Phase 3: Report Assembly

### VAPT-REPORT.md Structure

```markdown
# Vulnerability Assessment & Penetration Test Report

## Document Information
| Field | Value |
|-------|-------|
| Target | <url> |
| Date | <timestamp> |
| Tester | <from AUTHORIZATION-LOG.md> |
| Authorization | <from AUTHORIZATION-LOG.md> |
| Scope | <tested scope> |
| Mode | Pro / Dev |

---

## Executive Summary

<2-3 paragraph non-technical summary for stakeholders>
<Overall security posture rating>
<Key risk areas>
<Top priority actions>

---

## Security Posture Score: XX/100 (Rating)

### Category Breakdown

| Category | Weight | Score | Findings |
|----------|--------|-------|----------|
| Injection | 20% | XX/100 | X critical, X high, X medium |
| Authentication | 15% | XX/100 | ... |
| Authorization | 12% | XX/100 | ... |
| API Security | 12% | XX/100 | ... |
| SSL/TLS | 10% | XX/100 | ... |
| Security Headers | 8% | XX/100 | ... |
| Network Exposure | 8% | XX/100 | ... |
| Web App Surface | 7% | XX/100 | ... |
| Business Logic | 5% | XX/100 | ... |
| Recon Exposure | 3% | XX/100 | ... |

---

## Findings Summary

| # | Title | Severity | CVSS | CWE | Category |
|---|-------|----------|------|-----|----------|
| 1 | ... | Critical | 9.8 | CWE-89 | Injection |
| 2 | ... | High | 7.5 | CWE-639 | Authorization |
| ... | ... | ... | ... | ... | ... |

Total: X Critical, X High, X Medium, X Low, X Info

---

## Detailed Findings

### FINDING-001: <Title>

| Field | Value |
|-------|-------|
| Severity | Critical (CVSS 9.8) |
| CVSS Vector | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H |
| CWE | CWE-89 -- SQL Injection |
| OWASP | A03:2021 -- Injection |
| Affected URL | <url/path> |
| Parameter | <param name> |

**Description:**
<what the vulnerability is>

**Steps to Reproduce:**
1. <step 1>
2. <step 2>
3. <step 3>

**Evidence:**
<request/response or screenshot reference>

**Impact:**
<what an attacker can achieve>

**Remediation:**
<specific fix guidance with code examples in dev mode>

---

(Repeat for each finding, sorted by severity: Critical -> Info)

---

## Methodology

### Testing Approach
<brief description of methodology used>

### Waves Executed
| Wave | Phase | Status |
|------|-------|--------|
| Wave 1 | Reconnaissance | Completed / Skipped |
| Wave 2 | Scanning | Completed / Skipped |
| Wave 3 | Testing | Completed / Skipped |

### Tools Used
<list of tools used with versions>

---

## Scope and Limitations

### In Scope
<domains, paths, functionality tested>

### Out of Scope
<what was not tested and why>

### Skipped Tests
<tests skipped due to missing tools or --skip flag>

---

## Remediation Priority Matrix

### Immediate (Critical + High, < 1 week)
1. <finding with specific fix>
2. <finding with specific fix>

### Short-term (Medium, < 1 month)
1. <finding with specific fix>

### Long-term (Low + Info, ongoing)
1. <finding with improvement suggestion>

---

## Appendix

### A. Raw Tool Outputs
<condensed tool outputs for reference>

### B. CVSS Scoring Reference
<brief CVSS v3.1 explanation>

### C. Glossary
<terms used in this report>
```

## Dev Mode Additions

In dev mode, each finding's remediation section includes:
- Language-specific code fixes
- Configuration examples (nginx, Apache, etc.)
- Links to OWASP, CWE, and educational resources
- "Why this matters" explanation

## Pro Mode

In pro mode, the report is more compact:
- No educational explanations
- Shorter remediation (just the fix, not the why)
- Raw tool output in appendix
- Compact findings format
