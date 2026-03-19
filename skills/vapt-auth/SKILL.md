# Authentication & Session Testing

## When Invoked

The user runs `/vapt auth <url>` or this skill is triggered as part of Wave 3 during `/vapt audit`.

## Prerequisites

Check for existing context:
- If `VAPT-SCAN.md` exists → use discovered login pages and auth endpoints
- If `VAPT-WAVE2-CONTEXT.md` exists → use discovered services requiring auth
- If no context → look for `/login`, `/signin`, `/auth`, `/api/auth`, `/wp-login.php`

## Phase 1: Authentication Mechanism Analysis

### 1.1 Identify Auth Type

```bash
# Check for login forms
curl -sL <url>/login | grep -i '<form\|<input\|password\|username\|email'

# Check for HTTP auth
curl -sI <url>/admin | grep -i www-authenticate

# Check for API auth
curl -sI <url>/api | grep -i authorization
curl -sI <url>/api | grep -i x-api-key
```

Classify the authentication mechanism:
- Form-based (username/password)
- HTTP Basic/Digest Auth
- OAuth 2.0 / OpenID Connect
- JWT (Bearer tokens)
- API Key
- SAML/SSO
- Multi-factor authentication

### 1.2 Password Policy Analysis

If a registration form exists:
1. Attempt to register with weak passwords to discover the policy
2. Check minimum length, complexity requirements
3. Check for password strength meter
4. Check if common passwords are blocked

## Phase 2: Brute Force Resistance

### 2.1 Rate Limiting

Send 10 rapid login attempts with wrong credentials:
```bash
for i in $(seq 1 10); do
    curl -s -o /dev/null -w "%{http_code}" -X POST <url>/login -d "username=test&password=wrong$i"
done
```

Check:
- Does the server rate-limit after N failures?
- Is there an account lockout mechanism?
- Are CAPTCHA/challenge mechanisms triggered?
- Does the error message change (indicating lockout)?

### 2.2 Username Enumeration

Test if the application reveals valid usernames:
```bash
# Compare responses for valid vs invalid usernames
curl -s -X POST <url>/login -d "username=admin&password=wrong"
curl -s -X POST <url>/login -d "username=nonexistent12345&password=wrong"
```

Compare: response body, status code, response time, headers. Differences indicate username enumeration.

Also check:
- Registration endpoint (does it say "email already exists"?)
- Password reset (does it say "user not found"?)
- API responses with different error messages

### 2.3 Default Credentials

**Only test a small set of well-known defaults (not brute force):**
- admin/admin, admin/password, admin/123456
- root/root, root/password
- test/test, user/user, guest/guest
- CMS-specific defaults based on detected CMS

## Phase 3: Session Management

### 3.1 Session Token Analysis

After successful login (or by examining Set-Cookie headers):

```bash
curl -sI <url>/login -X POST -d "username=test&password=test" | grep -i set-cookie
```

Analyze tokens for:
- **Length:** Should be >= 128 bits (16+ characters)
- **Entropy:** Should appear random (no sequential patterns)
- **Predictability:** Collect 10+ tokens and check for patterns
- **Cookie flags:** HttpOnly, Secure, SameSite (checked in vapt-headers)

### 3.2 Session Fixation

1. Get a session token before authentication
2. Authenticate with that token
3. Check if the token changes after login

If the token remains the same → Session fixation vulnerability.

### 3.3 Session Expiration

- Does the session expire after a reasonable period of inactivity?
- Is the session invalidated server-side after logout?
- Can the old session token be reused after logout?

```bash
# Login, get token, logout, try to use old token
TOKEN=$(curl -s -c - <url>/login -X POST -d "..." | grep session)
curl -s <url>/logout -b "session=$TOKEN"
curl -s <url>/dashboard -b "session=$TOKEN"  # Should fail
```

## Phase 4: JWT Analysis

### 4.1 JWT Detection

If the application uses JWTs (in Authorization header or cookies):

```bash
# Decode JWT (header and payload are base64)
echo "<token>" | cut -d. -f1 | base64 -d 2>/dev/null
echo "<token>" | cut -d. -f2 | base64 -d 2>/dev/null
```

### 4.2 JWT Vulnerability Checks

| Check | Test Method | Severity |
|-------|-----------|----------|
| **Algorithm confusion** | Change alg to "none" and remove signature | Critical (9.8) |
| **Weak secret** | Attempt to crack with common wordlist | High (8.6) |
| **Algorithm switch** | Change RS256 to HS256, sign with public key | Critical (9.8) |
| **Missing expiration** | Check if `exp` claim exists | Medium (5.5) |
| **Sensitive data in payload** | Check for passwords, SSNs, etc. | Medium (5.0) |
| **Missing issuer/audience** | Check for `iss` and `aud` claims | Low (3.5) |

### 4.3 JWT none Algorithm

```bash
# Craft a JWT with algorithm "none"
# Header: {"alg":"none","typ":"JWT"}
# Payload: modify claims (e.g., change user role)
# Signature: empty
```

Try to access protected endpoints with the forged token.

## Phase 5: OAuth Testing

### 5.1 OAuth Flow Analysis

If OAuth is detected:

| Check | Test | Severity |
|-------|------|----------|
| `redirect_uri` manipulation | Change to attacker-controlled domain | High (7.4) |
| Missing `state` parameter | Check for CSRF in OAuth flow | Medium (6.5) |
| Open redirect in redirect_uri | Partial path manipulation | Medium (5.4) |
| Token leakage in URL | Check if token appears in URL fragment | Medium (5.0) |
| PKCE enforcement | Check if code_challenge is required | Medium (4.5) |

### 5.2 Redirect URI Testing

```bash
# Test redirect_uri manipulation
curl -sI "<oauth_url>?client_id=<id>&redirect_uri=https://evil.com&response_type=code"
curl -sI "<oauth_url>?client_id=<id>&redirect_uri=https://legit.com.evil.com&response_type=code"
curl -sI "<oauth_url>?client_id=<id>&redirect_uri=https://legit.com%40evil.com&response_type=code"
```

## Phase 6: MFA Analysis

If MFA is detected:

| Check | Severity |
|-------|----------|
| MFA can be skipped by direct URL access | Critical (9.1) |
| MFA code reuse (same code works twice) | High (7.5) |
| No rate limiting on MFA code entry | High (7.5) |
| MFA backup codes predictable | Medium (6.5) |
| MFA not enforced on all sensitive operations | Medium (5.0) |

## Phase 7: Password Reset

### 7.1 Reset Flow Analysis

| Check | Severity |
|-------|----------|
| Reset token predictable or sequential | Critical (9.1) |
| Reset token doesn't expire | High (7.5) |
| Reset token reusable | Medium (6.5) |
| Host header injection in reset email | High (7.4) |
| Username enumeration via reset | Low (3.7) |
| No rate limiting on reset requests | Medium (5.0) |

## Phase 8: Output

### Terminal Output

**Dev mode:** Explain each auth vulnerability, how it can be exploited, and best practices for secure authentication.

**Pro mode:** Findings table only.

### VAPT-AUTH.md

```markdown
# VAPT Authentication & Session Report

## Target: <url>
## Date: <timestamp>

## Authentication Mechanism
| Type | Details |
|------|---------|
| Method | ... |
| MFA | ... |
| Password Policy | ... |

## Brute Force Resistance
| Check | Status |
|-------|--------|
| Rate limiting | ... |
| Account lockout | ... |
| CAPTCHA | ... |
| Username enumeration | ... |

## Session Management
| Check | Status |
|-------|--------|
| Token entropy | ... |
| Session fixation | ... |
| Logout invalidation | ... |
| Cookie flags | ... |

## JWT Analysis (if applicable)
<findings>

## OAuth Analysis (if applicable)
<findings>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt authz <url> — test authorization controls
- /vapt inject <url> — test for injection via auth parameters
```

## Cross-Skill Integration

- Auth findings weight 15% in Security Posture Score
- Weak auth informs vapt-authz (easier to test access control with authenticated sessions)
- JWT findings inform vapt-api testing
