# Recon & OSINT

## When Invoked

The user runs `/vapt recon <url>` or this skill is triggered as part of Wave 1 during `/vapt audit`.

## Phase 1: Passive Reconnaissance

### 1.1 DNS Enumeration

Run DNS lookups for the target domain:

```bash
# A, AAAA, MX, TXT, NS, SOA, CNAME records
dig +short <domain> A
dig +short <domain> AAAA
dig +short <domain> MX
dig +short <domain> TXT
dig +short <domain> NS
dig +short <domain> SOA
dig +short <domain> CNAME
```

Look for:
- IP addresses and hosting provider
- Mail servers (potential phishing targets)
- TXT records (SPF, DKIM, DMARC — email security posture)
- NS records (DNS hosting, potential zone transfer)

### 1.2 Subdomain Enumeration

**If `subfinder` is installed:**
```bash
subfinder -d <domain> -silent
```

**If `amass` is installed:**
```bash
amass enum -passive -d <domain>
```

**Fallback (always run):**
- Query crt.sh for certificate transparency logs:
  ```bash
  curl -s "https://crt.sh/?q=%25.<domain>&output=json" | python3 -c "import sys,json; [print(x['name_value']) for x in json.load(sys.stdin)]" | sort -u
  ```
- Check common subdomains via DNS: www, mail, api, admin, staging, dev, test, app, portal, vpn, cdn, static, docs, blog

### 1.3 Technology Fingerprinting

**If `whatweb` is installed:**
```bash
whatweb -q <url>
```

**If `wafw00f` is installed:**
```bash
wafw00f <url>
```

**Fallback (always run):**
- Fetch homepage headers and body with curl:
  ```bash
  curl -sIL <url>
  curl -sL <url> | head -200
  ```
- Extract from response headers: Server, X-Powered-By, X-Generator
- Extract from HTML: meta generator tag, script/link src patterns, CSS class naming conventions
- Identify: Web server (nginx/Apache/IIS), language (PHP/Python/Node/Java/Ruby), framework (Laravel/Django/Express/Spring/Rails), CMS (WordPress/Drupal/Joomla), CDN (Cloudflare/AWS CloudFront/Akamai), WAF presence

### 1.4 WHOIS Analysis

```bash
whois <domain>
```

Extract:
- Registrar and registration date
- Expiration date (expired domains = risk)
- Registrant organization (privacy protection or exposed?)
- Name servers

### 1.5 Web Archive Exposure

Check Wayback Machine for historical snapshots:
```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=<domain>/*&output=json&fl=original&collapse=urlkey&limit=100"
```

Look for:
- Old admin panels or login pages
- Removed but archived sensitive pages
- Historical technology changes
- Previously exposed configuration files

### 1.6 Endpoint Discovery

```bash
# robots.txt
curl -s <url>/robots.txt

# sitemap.xml
curl -s <url>/sitemap.xml

# .well-known directory
curl -s <url>/.well-known/security.txt
curl -s <url>/.well-known/openid-configuration
```

Check for disallowed paths in robots.txt — these often point to sensitive areas.

### 1.7 Google Dorking Queries

Generate (but don't execute — present to user) Google dork queries:
- `site:<domain> filetype:pdf` — exposed documents
- `site:<domain> filetype:sql` — database dumps
- `site:<domain> filetype:env` — environment files
- `site:<domain> inurl:admin` — admin panels
- `site:<domain> inurl:login` — login pages
- `site:<domain> intitle:"index of"` — directory listings
- `site:<domain> ext:log` — log files
- `site:<domain> "password" filetype:txt` — credential files

## Phase 2: Analysis

### 2.1 Attack Surface Mapping

Compile all discovered assets into categories:
- **Domains & Subdomains:** list with IP addresses
- **Web Applications:** URLs with detected technology
- **Email Infrastructure:** MX records, SPF/DKIM/DMARC status
- **Exposed Services:** anything unusual in DNS/WHOIS
- **Sensitive Paths:** from robots.txt, archives, common paths

### 2.2 Risk Assessment

Score recon exposure findings:

| Finding | Severity | CVSS |
|---------|----------|------|
| Subdomain takeover possible | High | 7.5 |
| DNS zone transfer enabled | Medium | 5.3 |
| Sensitive files in web archive | Medium | 5.0 |
| Technology version disclosed | Low | 3.7 |
| WHOIS info not privacy-protected | Info | 0.0 |
| Excessive subdomains exposed | Info | 0.0 |

## Phase 3: Output

### Terminal Output

Display a summary table of discovered assets and any findings.

**Dev mode:** Explain what each discovery means for an attacker. Why subdomain enumeration matters. Why tech fingerprinting is the first step.

**Pro mode:** Just the asset list and findings table.

### VAPT-RECON.md

Write the full output to `VAPT-RECON.md`:

```markdown
# VAPT Reconnaissance Report

## Target: <domain>
## Date: <timestamp>

## DNS Records
<table of all DNS records>

## Subdomains Discovered
<list with IPs and status codes>

## Technology Stack
| Component | Detected |
|-----------|----------|
| Web Server | ... |
| Language | ... |
| Framework | ... |
| CMS | ... |
| CDN | ... |
| WAF | ... |

## WHOIS Summary
<key fields>

## Exposed Endpoints
<robots.txt disallowed paths, sitemap entries, .well-known>

## Web Archive Findings
<interesting historical URLs>

## Google Dorking Queries
<generated queries for manual follow-up>

## Findings
<table of scored findings>

## Suggested Next Steps
- /vapt network <url> — scan discovered IPs for open ports
- /vapt scan <url> — check detected CMS for known vulnerabilities
- /vapt ssl <url> — analyze SSL/TLS configuration
```

## Cross-Skill Integration

- Output feeds into Wave 2 via `VAPT-WAVE1-CONTEXT.md`
- Discovered subdomains expand the scope for all subsequent skills
- Technology fingerprints guide tool selection in vapt-scan and vapt-inject
