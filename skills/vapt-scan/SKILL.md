# Web Application Scanning

## When Invoked

The user runs `/vapt scan <url>` or this skill is triggered as part of Wave 2 during `/vapt audit`.

## Phase 1: Directory & File Discovery

### 1.1 Directory Brute-Forcing

**If `ffuf` is installed:**
```bash
ffuf -u <url>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -s
```

**If `feroxbuster` is installed:**
```bash
feroxbuster -u <url> -w /usr/share/wordlists/dirb/common.txt -s 200,301,302,403 --quiet
```

**If `dirsearch` is installed:**
```bash
dirsearch -u <url> -q
```

**Fallback (curl-based):**
Check a curated list of common paths:
```
/admin, /login, /dashboard, /wp-admin, /wp-login.php, /administrator,
/phpmyadmin, /cpanel, /webmail, /api, /api/v1, /api/v2, /graphql,
/swagger, /swagger-ui, /api-docs, /docs, /status, /health, /metrics,
/debug, /trace, /actuator, /env, /config, /backup, /test, /staging,
/.git, /.svn, /.env, /.htaccess, /.htpasswd, /web.config, /crossdomain.xml,
/sitemap.xml, /robots.txt, /server-status, /server-info
```

For each path, check with curl:
```bash
curl -sI -o /dev/null -w "%{http_code}" <url>/<path>
```

### 1.2 Backup & Config File Detection

Check for exposed sensitive files:
```
/.env, /.env.bak, /.env.old, /.env.production
/.git/config, /.git/HEAD
/.svn/entries
/web.config, /web.config.bak
/.htaccess, /.htpasswd
/wp-config.php.bak, /wp-config.php.old
/config.php.bak, /database.yml
/.DS_Store
/thumbs.db
/error_log, /debug.log
/dump.sql, /backup.sql, /db.sql
```

### 1.3 Information Disclosure

Check for verbose error pages:
```bash
# Trigger errors
curl -s "<url>/nonexistent-page-12345"
curl -s "<url>/?id='"
curl -s "<url>/%"
```

Look for: stack traces, framework versions, file paths, SQL errors, debug information.

## Phase 2: CMS Detection & Scanning

### 2.1 CMS Identification

Check for CMS indicators:

| CMS | Detection Method |
|-----|-----------------|
| WordPress | `/wp-login.php`, `/wp-admin/`, meta generator tag, `/wp-content/` |
| Drupal | `/core/CHANGELOG.txt`, `X-Generator: Drupal`, `/sites/default/` |
| Joomla | `/administrator/`, meta generator tag, `/media/system/` |
| Magento | `/admin/`, `/skin/frontend/`, cookie `frontend` |
| Shopify | `X-ShopId` header, `cdn.shopify.com` references |

### 2.2 CMS-Specific Scanning

**WordPress (if `wpscan` is installed):**
```bash
wpscan --url <url> --enumerate vp,vt,u --no-banner
```

**Fallback for WordPress:**
- Check `/wp-json/wp/v2/users` for user enumeration
- Check `/wp-json/` for API exposure
- Check `/xmlrpc.php` for XML-RPC (brute force vector)
- Check `readme.html` for version
- Enumerate plugins via `/wp-content/plugins/<name>/readme.txt`

**Drupal:**
- Check `/CHANGELOG.txt` for version
- Check `/user/register` for user registration
- Check for Drupalgeddon indicators

### 2.3 Version CVE Matching

Once CMS/framework version is identified:
1. Record the exact version
2. Check against known CVE databases
3. Flag any CVE with CVSS >= 7.0 as High
4. Flag any CVE with known exploits as Critical

## Phase 3: Automated Vulnerability Scanning

### 3.1 Nikto Scan

**If `nikto` is installed:**
```bash
nikto -h <url> -nointeractive -C all
```

Nikto checks for:
- Outdated server software
- Dangerous files/programs
- Server configuration issues
- Default installations

### 3.2 Nuclei Templates

**If `nuclei` is installed:**
```bash
# Critical and high severity templates only (for speed)
nuclei -u <url> -severity critical,high -silent
```

For full audit:
```bash
nuclei -u <url> -severity critical,high,medium -silent
```

### 3.3 Default Credential Checks

For discovered admin panels, check common defaults:
- admin/admin, admin/password, admin/12345
- root/root, root/toor
- test/test, user/user
- CMS-specific defaults (WordPress: admin/admin)

**Do not brute force.** Only check a small list of well-known defaults.

## Phase 4: Output

### Terminal Output

Display discovered paths, CMS info, and vulnerability findings.

**Dev mode:** Explain what each finding means, why exposed .git is dangerous, what an attacker can do with admin panel access.

**Pro mode:** Findings table with severity only.

### VAPT-SCAN.md

```markdown
# VAPT Web Application Scan

## Target: <url>
## Date: <timestamp>

## Discovered Paths
| Path | Status | Type |
|------|--------|------|
| /admin | 302 → /login | Admin panel |
| /api/v1 | 200 | API endpoint |
| /.git/config | 200 | Exposed git config |
| ... | ... | ... |

## CMS / Framework Detection
| Component | Version | Status |
|-----------|---------|--------|
| ... | ... | ... |

## Known CVEs
| CVE | CVSS | Description | Affected Version |
|-----|------|-------------|-----------------|
| ... | ... | ... | ... |

## Exposed Sensitive Files
<list of found backup/config files>

## Nikto / Nuclei Results
<parsed results>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt inject <url> — test discovered endpoints for injections
- /vapt auth <url> — test discovered login panels
- /vapt api <url> — test discovered API endpoints
```

## Cross-Skill Integration

- Discovered directories and endpoints feed into Wave 2 context
- Found API endpoints expand scope for vapt-api
- Login pages inform vapt-auth testing
- Parameter-accepting pages inform vapt-inject testing
