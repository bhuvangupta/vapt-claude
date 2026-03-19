# SSL/TLS & Cryptography Analysis

## When Invoked

The user runs `/vapt ssl <url>` or this skill is triggered as part of Wave 1 during `/vapt audit`.

## Phase 1: Certificate Analysis

### 1.1 Certificate Chain

**If `testssl.sh` or `testssl` is installed:**
```bash
testssl.sh --quiet --color 0 <domain>
```

**Fallback (always run):**
```bash
echo | openssl s_client -connect <domain>:443 -servername <domain> 2>/dev/null | openssl x509 -noout -text
```

Extract and analyze:
- **Issuer:** Who issued the cert (Let's Encrypt, DigiCert, self-signed?)
- **Subject / SAN:** What domains are covered
- **Validity:** Not Before / Not After — is it expired or expiring soon (<30 days)?
- **Key Size:** RSA 2048+ or ECDSA 256+? Anything below is weak
- **Signature Algorithm:** SHA-256 minimum. SHA-1 is broken.
- **Certificate Chain:** Is the full chain present? Missing intermediates?

### 1.2 Certificate Transparency

Check if certificate appears in CT logs (indicates proper issuance):
```bash
curl -s "https://crt.sh/?q=<domain>&output=json" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'{len(data)} certificates found in CT logs')"
```

## Phase 2: Protocol & Cipher Analysis

### 2.1 Protocol Versions

**If `sslscan` is installed:**
```bash
sslscan --no-colour <domain>
```

**Fallback:**
```bash
# Test each protocol version
for proto in ssl3 tls1 tls1_1 tls1_2 tls1_3; do
    echo | openssl s_client -connect <domain>:443 -$proto 2>&1 | grep -q "CONNECTED" && echo "$proto: ENABLED" || echo "$proto: DISABLED"
done
```

**Scoring:**

| Protocol | Status | Severity |
|----------|--------|----------|
| SSLv3 | Must be disabled | High (7.4) — POODLE |
| TLS 1.0 | Should be disabled | Medium (5.9) |
| TLS 1.1 | Should be disabled | Medium (5.3) |
| TLS 1.2 | Must be enabled | OK |
| TLS 1.3 | Should be enabled | Best practice |

### 2.2 Cipher Suites

```bash
# List supported ciphers
nmap --script ssl-enum-ciphers -p 443 <domain>
```

**Or with openssl:**
```bash
openssl s_client -connect <domain>:443 -cipher 'ALL:eNULL' 2>/dev/null
```

Flag as weak:
- RC4 ciphers (broken)
- DES/3DES ciphers (weak)
- Export-grade ciphers (40/56-bit)
- NULL ciphers (no encryption)
- Anonymous key exchange (no authentication)
- CBC mode ciphers with TLS 1.0 (BEAST)

Prefer:
- ECDHE key exchange (forward secrecy)
- AES-GCM or ChaCha20-Poly1305 (AEAD)
- SHA-256+ MAC

## Phase 3: Known Attack Testing

### 3.1 Vulnerability Checks

Test for known SSL/TLS attacks:

| Attack | Test Method | Severity |
|--------|------------|----------|
| **Heartbleed** (CVE-2014-0160) | `nmap --script ssl-heartbleed -p 443 <domain>` or `openssl s_client` with heartbeat extension | Critical (9.8) |
| **POODLE** (CVE-2014-3566) | SSLv3 enabled + CBC ciphers | High (7.4) |
| **BEAST** (CVE-2011-3389) | TLS 1.0 + CBC ciphers | Medium (4.3) |
| **DROWN** (CVE-2016-0800) | SSLv2 enabled on same key | High (7.4) |
| **ROBOT** | RSA key exchange enabled | Medium (5.9) |
| **Logjam** (CVE-2015-4000) | DH params < 2048 bits | Medium (4.3) |
| **FREAK** (CVE-2015-0204) | Export-grade RSA ciphers | High (7.4) |
| **Sweet32** (CVE-2016-2183) | 3DES/Blowfish 64-bit block ciphers | Medium (5.3) |

### 3.2 HSTS Analysis

```bash
curl -sI <url> | grep -i strict-transport
```

Check:
- Is HSTS header present?
- `max-age` value (should be >= 31536000 / 1 year)
- `includeSubDomains` directive present?
- Is domain on the HSTS preload list?

### 3.3 OCSP Stapling

```bash
echo | openssl s_client -connect <domain>:443 -status 2>/dev/null | grep -A 5 "OCSP Response"
```

### 3.4 Mixed Content

If the page is served over HTTPS, check if any resources are loaded over HTTP:
```bash
curl -sL <url> | grep -oP 'http://[^"'"'"'\s>]+' | head -20
```

## Phase 4: Output

### Terminal Output

Display a summary of SSL/TLS configuration with severity ratings.

**Dev mode:** Explain why each finding matters. What Heartbleed actually does. Why forward secrecy matters. How HSTS preload works.

**Pro mode:** Configuration matrix and findings table only.

### VAPT-SSL.md

```markdown
# VAPT SSL/TLS Analysis

## Target: <domain>
## Date: <timestamp>

## Certificate
| Field | Value |
|-------|-------|
| Issuer | ... |
| Subject | ... |
| SAN | ... |
| Valid From | ... |
| Valid Until | ... |
| Key Size | ... |
| Signature | ... |
| Chain Valid | ... |

## Protocol Support
| Protocol | Status |
|----------|--------|
| SSLv3 | ... |
| TLS 1.0 | ... |
| TLS 1.1 | ... |
| TLS 1.2 | ... |
| TLS 1.3 | ... |

## Cipher Suites
### Strong (Preferred)
<list>

### Weak (Should Disable)
<list>

## Known Vulnerabilities
<table with attack name, status, severity>

## HSTS
| Check | Status |
|-------|--------|
| Header Present | ... |
| max-age | ... |
| includeSubDomains | ... |
| Preload List | ... |

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt headers <url> — check all security headers
- /vapt scan <url> — check for web application vulnerabilities
```

## Cross-Skill Integration

- SSL findings feed into Wave 1 context via `VAPT-WAVE1-CONTEXT.md`
- Certificate SAN entries may reveal additional subdomains (feed back to recon)
- Weak SSL config informs vapt-headers assessment
