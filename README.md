<p align="center">
  <strong>VAPT Claude Code Skill</strong>
</p>

<p align="center">
  <strong>Full-spectrum web application security testing.</strong> Vulnerability Assessment and Penetration Testing<br/>
  powered by Claude Code — from reconnaissance to exploitation to remediation reporting.
</p>

<p align="center">
  Automate what's automatable. Guide what requires human judgment. Report everything professionally.
</p>

---

## Quick Start

### One-Command Install (macOS/Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/vapt-claude/main/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/YOUR_USERNAME/vapt-claude.git
cd vapt-claude
./install.sh
```

### Requirements

- Python 3.8+
- Claude Code CLI
- Git

### Security Tool Dependencies

VAPT skills work best with external security tools installed. Run the dependency checker:

```
/vapt setup
```

This checks for all tools and provides install commands. Tools are organized in three tiers:

| Tier | Tools | When Missing |
|------|-------|-------------|
| **Core** | `curl`, `openssl`, `python3`, `nmap` | Strong warning — many tests degraded |
| **Recommended** | `sqlmap`, `nuclei`, `ffuf`, `subfinder`, `nikto`, `testssl.sh` | Graceful degradation — uses curl/Python fallbacks |
| **Optional** | `hydra`, `wpscan`, `amass`, `masscan`, `dalfox`, `feroxbuster`, `websocat`, `wscat` | Skips specific sub-tests, noted in report |

**Quick tool install (macOS with Homebrew):**

```bash
# Core
brew install nmap openssl python3

# Recommended
pip install sqlmap
brew install nikto
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
brew install testssl

# Optional
brew install hydra
gem install wpscan
go install github.com/owasp-amass/amass/v4/...@master
brew install masscan
go install github.com/hahwul/dalfox/v2@latest
brew install feroxbuster
brew install websocat
npm install -g wscat
```

**Quick tool install (Debian/Ubuntu):**

```bash
# Core
sudo apt install nmap openssl python3 python3-pip curl

# Recommended
pip install sqlmap
sudo apt install nikto
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
git clone --depth 1 https://github.com/drwetter/testssl.sh.git

# Optional
sudo apt install hydra
gem install wpscan
go install github.com/owasp-amass/amass/v4/...@master
sudo apt install masscan
go install github.com/hahwul/dalfox/v2@latest
sudo apt install feroxbuster
cargo install websocat
npm install -g wscat
```

> **Note:** All tools degrade gracefully. You can start testing immediately with just the core tools installed. The skill will use `curl` and Python fallbacks for anything missing.

---

## Commands

Open Claude Code and use these commands:

| Command | What It Does | Output |
|---------|-------------|--------|
| `/vapt audit <url>` | Full VAPT audit (all 3 waves) | `VAPT-AUDIT.md` |
| `/vapt recon <url>` | Recon & OSINT | `VAPT-RECON.md` |
| `/vapt network <url>` | Network & port scanning | `VAPT-NETWORK.md` |
| `/vapt ssl <url>` | SSL/TLS & crypto analysis | `VAPT-SSL.md` |
| `/vapt scan <url>` | Web app scanning & CVE matching | `VAPT-SCAN.md` |
| `/vapt inject <url>` | Injection testing (SQLi, XSS, SSTI, etc.) | `VAPT-INJECT.md` |
| `/vapt auth <url>` | Authentication & session testing | `VAPT-AUTH.md` |
| `/vapt authz <url>` | Authorization & access control | `VAPT-AUTHZ.md` |
| `/vapt api <url>` | API security testing | `VAPT-API.md` |
| `/vapt headers <url>` | Security headers & infrastructure | `VAPT-HEADERS.md` |
| `/vapt logic <url>` | Business logic testing | `VAPT-LOGIC.md` |
| `/vapt graphql <url>` | Deep GraphQL security testing | `VAPT-GRAPHQL.md` |
| `/vapt websocket <url>` | WebSocket security testing | `VAPT-WEBSOCKET.md` |
| `/vapt cloud <url>` | Cloud misconfiguration testing | `VAPT-CLOUD.md` |
| `/vapt report <url>` | Generate Markdown report | `VAPT-REPORT.md` |
| `/vapt report-pdf <url>` | Generate PDF report | `VAPT-REPORT.pdf` |
| `/vapt setup` | Check tool dependencies | Terminal output |

### Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--mode pro` | Terse output, advanced tool flags, no explanations | — |
| `--mode dev` | Educational output, explains findings, remediation snippets | Default |
| `--scope <domains>` | Limit testing to specific subdomains/paths | Full target |
| `--skip <category>` | Skip specific test categories during full audit | None |
| `--severity <min>` | Only report findings above threshold (critical/high/medium/low) | All |

### Examples

```bash
# Full audit in dev mode (educational)
/vapt audit https://example.com

# Full audit in pro mode (terse, advanced)
/vapt audit https://example.com --mode pro

# Just recon and SSL check
/vapt recon https://example.com
/vapt ssl https://example.com

# Injection testing scoped to API endpoints only
/vapt inject https://example.com --scope api.example.com

# Deep GraphQL testing
/vapt graphql https://example.com/graphql

# WebSocket security analysis
/vapt websocket https://example.com

# Cloud misconfiguration scan (S3, Azure Blob, GCS, Firebase)
/vapt cloud https://example.com

# Full audit but skip network scanning and business logic
/vapt audit https://example.com --skip network,logic

# Only show high and critical findings
/vapt audit https://example.com --severity high

# Generate PDF report from previous audit data
/vapt report-pdf https://example.com
```

---

## Architecture

```
vapt-claude/
├── vapt/SKILL.md                        # Main orchestrator (routes all /vapt commands)
│
├── skills/                              # 17 sub-skills
│   ├── vapt-recon/SKILL.md              # Recon & OSINT
│   ├── vapt-network/SKILL.md            # Network & port scanning
│   ├── vapt-ssl/SKILL.md                # SSL/TLS & cryptography
│   ├── vapt-scan/SKILL.md               # Web application scanning
│   ├── vapt-inject/SKILL.md             # Injection testing (SQLi, XSS, SSTI, etc.)
│   ├── vapt-auth/SKILL.md               # Authentication & session testing
│   ├── vapt-authz/SKILL.md              # Authorization & access control
│   ├── vapt-api/SKILL.md                # API security testing (REST)
│   ├── vapt-graphql/SKILL.md            # Deep GraphQL security testing
│   ├── vapt-websocket/SKILL.md          # WebSocket security testing
│   ├── vapt-cloud/SKILL.md              # Cloud misconfiguration testing
│   ├── vapt-headers/SKILL.md            # Security headers & infrastructure
│   ├── vapt-logic/SKILL.md              # Business logic testing
│   ├── vapt-report/SKILL.md             # Markdown report generation
│   ├── vapt-report-pdf/SKILL.md         # PDF report generation
│   └── vapt-setup/SKILL.md              # Tool dependency checker
│
├── agents/                              # 7 parallel subagents (wave-based)
│   ├── vapt-passive-recon.md            # Wave 1: OSINT, DNS, WHOIS, tech stack
│   ├── vapt-surface-mapper.md           # Wave 1: SSL/TLS, headers, security config
│   ├── vapt-service-scanner.md          # Wave 2: Ports, services, versions
│   ├── vapt-webapp-scanner.md           # Wave 2: Directories, CMS, known CVEs
│   ├── vapt-vuln-tester.md              # Wave 3: SQLi, XSS, SSTI, command injection
│   ├── vapt-auth-tester.md              # Wave 3: Auth bypass, session, IDOR
│   └── vapt-logic-tester.md             # Wave 3: API security, business logic, races
│
├── scripts/                             # Python utilities
│   ├── vapt_report_pdf.py               # PDF report generator (ReportLab)
│   └── vapt_cvss.py                     # CVSS v3.1 score calculator
│
├── templates/                           # Report templates
│   ├── executive-summary.md             # Executive summary template
│   ├── finding-template.md              # Per-finding report template
│   └── remediation-guide.md             # Common vulnerability fixes
│
├── install.sh                           # One-command installer
├── uninstall.sh                         # Clean uninstaller
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## How It Works

### Authorization Gate

Before ANY scan runs, the skill verifies you have authorization to test the target:

```
/vapt audit https://example.com

VAPT Authorization Required
============================
Target: example.com
Scope:  *.example.com

Do you have written authorization to test this target?

  [1] Pentest engagement (signed SOW/contract)
  [2] Bug bounty program
  [3] Own infrastructure
  [4] CTF / lab environment

Select (1-4):
```

Your authorization is logged to `AUTHORIZATION-LOG.md` with timestamp, scope, and basis. Subsequent commands against the same target in the same session skip the prompt.

### Full Audit Flow (Wave-Based Pipeline)

When you run `/vapt audit https://example.com`:

```
Wave 1 — Reconnaissance (parallel)
├── Passive recon agent (OSINT, DNS, WHOIS, tech stack)
├── Surface mapper agent (SSL/TLS, headers, security config)
└── Output: subdomains, endpoints, tech stack, certificates
     ↓ findings feed into ↓

Wave 2 — Scanning (parallel)
├── Service scanner agent (ports, services, versions)
├── Web app scanner agent (directories, CMS, known CVEs)
└── Output: open ports, services, directories, CVE matches
     ↓ findings feed into ↓

Wave 3 — Testing (parallel)
├── Vulnerability tester agent (SQLi, XSS, SSTI, command injection)
├── Auth tester agent (auth bypass, session, IDOR, privilege escalation)
├── Logic tester agent (API security, business logic, race conditions)
└── Output: confirmed vulnerabilities with CVSS scores
     ↓ all findings ↓

Wave 4 — Reporting (sequential)
└── Compile findings → VAPT-AUDIT.md + Security Posture Score
```

Each wave passes context files to the next, so later phases test endpoints and services discovered by earlier phases.

### Standalone Skill Usage

Each skill works independently too. Run them in any order:

```bash
/vapt recon https://example.com    # discover attack surface
/vapt ssl https://example.com      # check SSL/TLS config
/vapt inject https://example.com   # test for injections
/vapt report https://example.com   # compile whatever findings exist
```

Skills check for existing context files from previous runs. If you run `/vapt recon` first, then `/vapt inject` uses the discovered endpoints for smarter targeting.

### Mode System

**Dev Mode** (default) — educational, explains findings:
```
[CRITICAL] SQL Injection Found
  URL: /api/users?id=1' OR '1'='1
  CVSS: 10.0 (Critical) | CWE-89

  What happened: The 'id' parameter passes user input directly
  into a SQL query without sanitization. An attacker can extract,
  modify, or delete the entire database.

  How to fix:
    // Vulnerable
    db.query("SELECT * FROM users WHERE id = " + req.params.id)
    // Fixed
    db.query("SELECT * FROM users WHERE id = $1", [req.params.id])

  Learn more: https://owasp.org/Top10/A03_2021-Injection/
```

**Pro Mode** (`--mode pro`) — terse, for experienced pentesters:
```
[CRITICAL] SQLi — /api/users?id=1' OR '1'='1
  CVSS: 10.0 | CWE-89 | sqlmap --dbs confirmed
  Fix: Parameterized queries
```

---

## Scoring Methodology

### Individual Findings — CVSS v3.1

Each confirmed vulnerability gets a CVSS vector string and severity rating:

| Rating | CVSS Range | Meaning |
|--------|-----------|---------|
| Critical | 9.0 - 10.0 | Immediate exploitation risk |
| High | 7.0 - 8.9 | Significant security impact |
| Medium | 4.0 - 6.9 | Moderate risk, should fix |
| Low | 0.1 - 3.9 | Minor issue, fix when possible |
| Info | 0.0 | Informational, no direct risk |

### Security Posture Score (0-100)

Composite score weighted across all testing categories:

| Category | Weight | What Reduces Score |
|----------|--------|--------------------|
| Injection | 20% | Confirmed SQLi, XSS, SSTI, command injection |
| Authentication | 15% | Weak sessions, JWT flaws, brute-forceable logins |
| Authorization | 12% | IDOR, privilege escalation, forced browsing |
| API Security | 12% | BOLA, mass assignment, introspection leaks |
| SSL/TLS | 10% | Weak ciphers, expired certs, old protocols |
| Security Headers | 8% | Missing CSP, HSTS, clickjacking protection |
| Network Exposure | 8% | Unnecessary open ports, info disclosure |
| Web App Surface | 7% | Exposed admin panels, default creds, known CVEs |
| Business Logic | 5% | Race conditions, workflow bypass |
| Recon Exposure | 3% | Excessive DNS/WHOIS exposure, tech stack leaks |

**Score interpretation:**

| Range | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Minimal attack surface, strong controls |
| 70-89 | Good | Some issues, no critical exposure |
| 50-69 | Fair | Significant gaps, remediation needed |
| 30-49 | Poor | Serious vulnerabilities present |
| 0-29 | Critical | Immediate action required |

---

## Output Files

All outputs are written to the current working directory:

| File | Generated By | Contents |
|------|-------------|----------|
| `AUTHORIZATION-LOG.md` | Authorization gate | Audit trail of authorized targets |
| `VAPT-RECON.md` | `/vapt recon` | Subdomains, DNS, tech stack, OSINT |
| `VAPT-NETWORK.md` | `/vapt network` | Open ports, services, OS fingerprint |
| `VAPT-SSL.md` | `/vapt ssl` | Certificate, protocols, ciphers, attacks |
| `VAPT-SCAN.md` | `/vapt scan` | Directories, CMS, CVEs, exposed files |
| `VAPT-INJECT.md` | `/vapt inject` | SQLi, XSS, SSTI, command injection findings |
| `VAPT-AUTH.md` | `/vapt auth` | Session, JWT, OAuth, brute force findings |
| `VAPT-AUTHZ.md` | `/vapt authz` | IDOR, privilege escalation, access control |
| `VAPT-API.md` | `/vapt api` | API endpoint security, BOLA, REST |
| `VAPT-GRAPHQL.md` | `/vapt graphql` | GraphQL schema, introspection, batching, DoS |
| `VAPT-WEBSOCKET.md` | `/vapt websocket` | WebSocket auth, CSWSH, message injection |
| `VAPT-CLOUD.md` | `/vapt cloud` | S3 buckets, IMDS, subdomain takeover, CDN bypass |
| `VAPT-HEADERS.md` | `/vapt headers` | Security headers, CORS, server config |
| `VAPT-LOGIC.md` | `/vapt logic` | Race conditions, workflow bypass, abuse |
| `VAPT-AUDIT.md` | `/vapt audit` | Full audit with all findings + composite score |
| `VAPT-REPORT.md` | `/vapt report` | Client-ready Markdown report |
| `VAPT-REPORT.pdf` | `/vapt report-pdf` | Professional PDF report |
| `VAPT-WAVE1-CONTEXT.md` | Wave 1 (internal) | Intermediate context for wave 2 |
| `VAPT-WAVE2-CONTEXT.md` | Wave 2 (internal) | Intermediate context for wave 3 |
| `VAPT-WAVE3-FINDINGS.md` | Wave 3 (internal) | All findings for report generation |

---

## Use Cases

### For Pentest Engagements
- Run `/vapt audit` for comprehensive automated coverage
- Use individual skills to deep-dive specific areas
- Generate `/vapt report-pdf` as a professional client deliverable
- Authorization log provides audit trail documentation

### For Bug Bounty Hunters
- Start with `/vapt recon` to map the attack surface
- Target specific areas: `/vapt inject`, `/vapt api`, `/vapt auth`
- Deep-dive APIs with `/vapt graphql` and `/vapt websocket`
- Check cloud misconfigs with `/vapt cloud` (S3 buckets, Firebase, subdomain takeover)
- Use `--mode pro` for fast, terse output
- Chain skills: recon first, then targeted testing

### For DevSecOps / Developers
- Use `--mode dev` (default) to learn about each vulnerability class
- Run `/vapt headers` and `/vapt ssl` as part of deployment checklist
- Integrate `/vapt scan` into pre-release security reviews
- Check `/vapt cloud` before deploying to AWS/Azure/GCP
- Audit GraphQL and WebSocket endpoints with dedicated skills
- Remediation guidance includes actual code fixes

### For CTF Competitions
- Rapid recon with `/vapt recon`
- Targeted injection and auth testing
- `--mode pro` for speed

### For Compliance / Auditing
- Full `/vapt audit` covers OWASP Top 10, PCI-DSS requirements
- Generated reports map findings to CWE IDs
- Authorization log satisfies audit trail requirements
- Security Posture Score tracks improvement over time

---

## Ethical Use & Authorization

This tool performs **active penetration testing** including port scanning, injection testing, brute forcing, and exploitation attempts. **You must have explicit written authorization before testing any target.**

Acceptable authorization contexts:
- Signed penetration testing Statement of Work (SOW)
- Bug bounty program (within defined scope)
- Your own infrastructure
- CTF / lab environments

The authorization gate enforces this before every new target. All authorizations are logged to `AUTHORIZATION-LOG.md`.

**Unauthorized testing of systems you don't own or have permission to test is illegal in most jurisdictions.**

---

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm -rf ~/.claude/skills/vapt*
rm -f ~/.claude/agents/vapt-*.md
```

---

## License

MIT License

---

## Contributing

Contributions welcome! Please ensure any new testing modules follow the existing skill structure pattern.

---

Built for authorized security testing.
