# Injection Testing

## When Invoked

The user runs `/vapt inject <url>` or this skill is triggered as part of Wave 3 during `/vapt audit`.

## Prerequisites

Check for existing context:
- If `VAPT-WAVE2-CONTEXT.md` exists -> use discovered endpoints and parameters
- If `VAPT-SCAN.md` exists -> extract parameter-accepting URLs
- If no context -> run minimal endpoint discovery (crawl homepage links, check robots.txt)

## Phase 1: Parameter Discovery

### 1.1 Endpoint Crawling

```bash
# Extract links from homepage
curl -sL <url> | grep -oP 'href="[^"]*"' | sed 's/href="//;s/"//' | sort -u

# Extract form actions and input names
curl -sL <url> | grep -oP '<form[^>]*action="[^"]*"'
curl -sL <url> | grep -oP '<input[^>]*name="[^"]*"'
```

### 1.2 Parameter Identification

**If `arjun` is installed:**
```bash
arjun -u <url> -m GET,POST
```

**Fallback:** Extract parameters from:
- URL query strings
- Form fields (GET and POST)
- JSON request bodies (from API endpoints)
- HTTP headers (Host, Referer, X-Forwarded-For)
- Cookie values

Compile a target list: `[{url, method, parameter, location}]`

## Phase 2: SQL Injection Testing

### 2.1 Detection

**If `sqlmap` is installed:**
```bash
# Test a single URL with parameters
sqlmap -u "<url>?param=value" --batch --level 3 --risk 2 --threads 4

# For POST data
sqlmap -u "<url>" --data "param=value" --batch --level 3 --risk 2
```

Pro mode uses higher levels:
```bash
sqlmap -u "<url>?param=value" --batch --level 5 --risk 3 --threads 10 --tamper=space2comment
```

**Fallback (curl-based detection):**

Test each parameter with these payloads and compare responses:
- Single quote `'` (error-based detection)
- Boolean conditions: `OR 1=1` vs `OR 1=2`
- Time delays: `SLEEP(3)` or `WAITFOR DELAY`
- UNION probes: `UNION SELECT NULL`

Compare response length and time to baseline. Significant differences indicate potential injection.

### 2.2 Confirmation

If a potential SQLi is detected:
1. Verify with a true/false comparison
2. Confirm the DBMS type if possible
3. Do NOT extract sensitive data -- just prove the vulnerability exists
4. Record the payload, injection point, and evidence

### 2.3 Scoring

| Type | Severity | CVSS |
|------|----------|------|
| UNION-based SQLi | Critical | 9.8 |
| Error-based SQLi | Critical | 9.8 |
| Blind boolean SQLi | Critical | 9.1 |
| Blind time-based SQLi | High | 8.6 |
| Second-order SQLi | Critical | 9.8 |

## Phase 3: Cross-Site Scripting (XSS)

### 3.1 Reflected XSS

**If `dalfox` is installed:**
```bash
dalfox url "<url>?param=test" --silence --no-color
```

**Fallback (curl-based):**

Inject test payloads and check if they appear reflected unencoded in the response body:
- Script tag payloads
- Event handler payloads (onerror, onload)
- SVG-based payloads
- JavaScript URI payloads

For each parameter:
1. Send payload
2. Check if payload appears in response body unencoded
3. Check context (HTML body, attribute, JavaScript block, URL)

### 3.2 Stored XSS

Test on input fields that persist data (comments, profiles, messages):
1. Submit a canary payload with unique identifier
2. Check if it renders on subsequent page loads
3. Verify execution context

### 3.3 DOM-based XSS

Analyze client-side JavaScript for dangerous data flow patterns. Check for unsanitized user-controllable sources (URL hash, query params, referrer) flowing into DOM manipulation sinks (innerHTML, dynamic script creation, timer callbacks). See OWASP DOM-based XSS Prevention Cheat Sheet for the full source/sink taxonomy.

### 3.4 Scoring

| Type | Severity | CVSS |
|------|----------|------|
| Stored XSS | High | 8.1 |
| Reflected XSS (no CSP) | High | 7.1 |
| Reflected XSS (with CSP) | Medium | 5.4 |
| DOM-based XSS | Medium | 6.1 |

## Phase 4: Server-Side Template Injection (SSTI)

### 4.1 Detection

**If `tplmap` is installed:**
```bash
python3 tplmap.py -u "<url>?param=value"
```

**Fallback:** Test with template engine polyglot payloads:
```
{{7*7}} -- Jinja2, Twig
${7*7} -- Freemarker, Velocity
#{7*7} -- Ruby ERB
<%= 7*7 %> -- EJS, ERB
```

If `49` appears in the response, SSTI is confirmed.

### 4.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| SSTI confirmed (RCE possible) | Critical | 9.8 |
| SSTI confirmed (sandboxed) | High | 7.5 |

## Phase 5: Command Injection

### 5.1 Detection

**If `commix` is installed:**
```bash
commix --url="<url>?param=value" --batch
```

**Fallback:** Test with time-based payloads using sleep commands, pipe operators, backtick substitution, and subshell syntax. Measure response time -- delays beyond 5 seconds indicate command injection.

### 5.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| OS command injection confirmed | Critical | 9.8 |
| Blind command injection (time-based) | Critical | 9.1 |

## Phase 6: XXE (XML External Entity)

### 6.1 Detection

For endpoints accepting XML input, test with DTD entity declarations that reference external resources (file:// or http:// protocol handlers).

Check if entities are resolved in the response body.

For blind XXE, use out-of-band detection if the user has an OOB server.

### 6.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| XXE with file read | High | 7.5 |
| XXE with SSRF | High | 8.6 |
| Blind XXE confirmed | Medium | 5.3 |

## Phase 7: Header Injection

### 7.1 Host Header Injection

```bash
curl -sI -H "Host: evil.com" <url>
curl -sI -H "X-Forwarded-Host: evil.com" <url>
```

Check if the injected host appears in response headers (Location, links).

### 7.2 CRLF Injection

Test URL with encoded CR/LF characters (%0d%0a) to check if response headers can be injected.

### 7.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Host header injection (password reset poisoning) | High | 7.4 |
| CRLF injection | Medium | 5.4 |

## Phase 8: Output

### Terminal Output

**Dev mode:** For each injection type, explain the vulnerability, show the payload that worked, the impact, and how to fix it with code examples.

**Pro mode:** Findings table with injection type, URL, parameter, payload, CVSS.

### VAPT-INJECT.md

```markdown
# VAPT Injection Testing Report

## Target: <url>
## Date: <timestamp>
## Parameters Tested: <count>

## SQL Injection
<findings or "No SQL injection found">

## Cross-Site Scripting (XSS)
<findings or "No XSS found">

## Server-Side Template Injection
<findings or "No SSTI found">

## Command Injection
<findings or "No command injection found">

## XXE
<findings or "No XXE found">

## Header Injection
<findings or "No header injection found">

## Summary
| Type | Findings | Highest Severity |
|------|----------|-----------------|
| SQLi | ... | ... |
| XSS | ... | ... |
| SSTI | ... | ... |
| CMDi | ... | ... |
| XXE | ... | ... |
| Header | ... | ... |

## Suggested Next Steps
- /vapt auth <url> -- test authentication mechanisms
- /vapt authz <url> -- test access controls on vulnerable endpoints
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- Injection findings are the highest-weight category (20%) in Security Posture Score
- Confirmed injections inform vapt-authz (can injection escalate privileges?)
- Injection points feed into vapt-logic (can injection bypass business rules?)
