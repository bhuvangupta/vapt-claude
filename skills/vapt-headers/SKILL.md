# Infrastructure & Security Headers

## When Invoked

The user runs `/vapt headers <url>` or this skill is triggered as part of Wave 1 during `/vapt audit`.

## Phase 1: Header Collection

### 1.1 Fetch Response Headers

```bash
curl -sIL <url>
```

Also check specific paths:
```bash
curl -sI <url>/login 2>/dev/null
curl -sI <url>/api 2>/dev/null
curl -sI <url>/admin 2>/dev/null
```

### 1.2 Extract All Security-Relevant Headers

Parse the response for each of these headers (case-insensitive):

**Security Headers:**
- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `Strict-Transport-Security`
- `Referrer-Policy`
- `Permissions-Policy`
- `X-XSS-Protection`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`
- `Cross-Origin-Embedder-Policy`

**CORS Headers:**
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`
- `Access-Control-Allow-Credentials`

**Information Disclosure:**
- `Server`
- `X-Powered-By`
- `X-AspNet-Version`
- `X-AspNetMvc-Version`
- `X-Generator`

**Cache Headers (on sensitive pages):**
- `Cache-Control`
- `Pragma`
- `Expires`

## Phase 2: Header Analysis

### 2.1 Content-Security-Policy (CSP)

| Check | Severity if Failed |
|-------|-------------------|
| CSP header present | Medium (5.0) |
| No `unsafe-inline` in script-src | Medium (5.5) |
| No `unsafe-eval` in script-src | Medium (5.5) |
| No wildcard `*` in default-src | Medium (4.5) |
| `frame-ancestors` defined | Medium (4.5) |
| Reports configured (report-uri/report-to) | Info (0.0) |

### 2.2 X-Frame-Options / frame-ancestors

| Check | Severity if Failed |
|-------|-------------------|
| X-Frame-Options or CSP frame-ancestors present | Medium (4.3) — clickjacking |
| Value is DENY or SAMEORIGIN (not ALLOW-FROM *) | Medium (4.3) |

### 2.3 HSTS

| Check | Severity if Failed |
|-------|-------------------|
| Strict-Transport-Security present | Medium (5.0) |
| max-age >= 31536000 (1 year) | Low (3.5) |
| includeSubDomains directive | Low (2.5) |
| On HSTS preload list | Info (0.0) |

### 2.4 Other Security Headers

| Header | Expected | Severity if Missing |
|--------|----------|-------------------|
| X-Content-Type-Options | `nosniff` | Low (3.1) |
| Referrer-Policy | `strict-origin-when-cross-origin` or stricter | Low (2.5) |
| Permissions-Policy | Restrict camera, microphone, geolocation | Low (2.0) |
| X-XSS-Protection | `0` (modern best practice — rely on CSP) | Info (0.0) |

### 2.5 CORS Analysis

| Check | Severity if Failed |
|-------|-------------------|
| `Access-Control-Allow-Origin: *` with credentials | High (8.1) |
| Origin reflection without validation | High (7.5) |
| `null` origin allowed | Medium (6.1) |
| Overly permissive methods (PUT, DELETE on public endpoints) | Medium (5.0) |

Test CORS by sending request with crafted Origin:
```bash
curl -sI -H "Origin: https://evil.com" <url> | grep -i access-control
```

### 2.6 Information Disclosure

| Finding | Severity |
|---------|----------|
| Server header reveals version (e.g., `Apache/2.4.49`) | Low (3.7) |
| X-Powered-By reveals framework version | Low (3.5) |
| X-AspNet-Version present | Low (3.5) |
| Detailed error pages with stack traces | Medium (5.3) |

### 2.7 HTTP Methods

```bash
curl -sI -X OPTIONS <url> | grep -i allow
```

Check if dangerous methods are enabled:
- `TRACE` — can enable Cross-Site Tracing (XST)
- `PUT` / `DELETE` — on static content paths
- `CONNECT` — proxy abuse

### 2.8 Cookie Security

```bash
curl -sI <url> | grep -i set-cookie
```

For each cookie, check:

| Flag | Expected | Severity if Missing |
|------|----------|-------------------|
| `HttpOnly` | Present on session cookies | Medium (4.5) |
| `Secure` | Present on all cookies (HTTPS site) | Medium (4.5) |
| `SameSite` | `Strict` or `Lax` | Low (3.5) |
| Path | Scoped appropriately | Low (2.0) |

### 2.9 Cache-Control on Sensitive Pages

Check login pages, account pages, API responses for:
- `Cache-Control: no-store` (sensitive data should not be cached)
- `Pragma: no-cache` (for HTTP/1.0 compatibility)

## Phase 3: Output

### Terminal Output

Display a header scorecard:

**Dev mode:** Explain each header's purpose, show what a properly configured header looks like, provide copy-paste nginx/Apache config.

**Pro mode:** Pass/fail table only.

### VAPT-HEADERS.md

```markdown
# VAPT Security Headers Analysis

## Target: <url>
## Date: <timestamp>

## Header Scorecard

| Header | Status | Value | Severity |
|--------|--------|-------|----------|
| Content-Security-Policy | ... | ... | ... |
| X-Frame-Options | ... | ... | ... |
| X-Content-Type-Options | ... | ... | ... |
| Strict-Transport-Security | ... | ... | ... |
| Referrer-Policy | ... | ... | ... |
| Permissions-Policy | ... | ... | ... |

## CORS Configuration
<analysis results>

## Information Disclosure
<server/version headers found>

## Cookie Security
| Cookie | HttpOnly | Secure | SameSite | Path |
|--------|----------|--------|----------|------|
| ... | ... | ... | ... | ... |

## HTTP Methods
<allowed methods per endpoint>

## Findings
<scored findings table>

## Recommended Configuration

### Nginx
<copy-paste header config>

### Apache
<copy-paste header config>

## Suggested Next Steps
- /vapt ssl <url> — analyze SSL/TLS configuration
- /vapt scan <url> — check for web application vulnerabilities
```

## Cross-Skill Integration

- Security header findings feed into Wave 1 context
- CSP analysis informs XSS testing strategy in vapt-inject (weak CSP = higher XSS impact)
- CORS findings inform vapt-api cross-origin testing
