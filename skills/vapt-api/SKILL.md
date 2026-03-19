# API Security Testing

## When Invoked

The user runs `/vapt api <url>` or this skill is triggered as part of Wave 3 during `/vapt audit`.

## Prerequisites

Check for existing context:
- If `VAPT-WAVE2-CONTEXT.md` exists -> use discovered API endpoints
- If `VAPT-SCAN.md` exists -> extract API paths from scan results
- If no context -> discover API endpoints via common paths

## Phase 1: API Discovery

### 1.1 OpenAPI / Swagger Detection

```bash
# Common OpenAPI spec locations
for path in /swagger.json /swagger-ui /openapi.json /api-docs /api/v1/swagger.json /api/docs /v1/api-docs /v2/api-docs /api/swagger /docs/api; do
    code=$(curl -s -o /dev/null -w "%{http_code}" <url>$path)
    [ "$code" != "404" ] && echo "Found: $path ($code)"
done
```

If a spec file is found, parse it to extract all endpoints, methods, and parameters.

### 1.2 GraphQL Detection

```bash
# Common GraphQL endpoints
for path in /graphql /graphiql /v1/graphql /api/graphql /query; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"query":"{__typename}"}' <url>$path)
    [ "$code" = "200" ] && echo "GraphQL found: $path"
done
```

### 1.3 API Endpoint Fuzzing

**If `kiterunner` is installed:**
```bash
kr scan <url> -w /path/to/routes-large.kite
```

**If `ffuf` is installed:**
```bash
ffuf -u <url>/api/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,201,401,403
```

**Fallback:** Check common API path patterns:
```
/api, /api/v1, /api/v2, /api/v3
/api/users, /api/admin, /api/config
/api/health, /api/status, /api/metrics
/api/search, /api/export, /api/import
```

## Phase 2: Authentication Testing

### 2.1 Unauthenticated Access

Test all discovered endpoints without authentication:
```bash
for endpoint in <discovered_endpoints>; do
    echo "$endpoint: $(curl -s -o /dev/null -w '%{http_code}' <url>$endpoint)"
done
```

Endpoints that return 200 without auth may be misconfigured.

### 2.2 API Key / Token Analysis

If API keys are used:
- Check if keys are in URLs (leakable via logs/referrer)
- Check key rotation / expiration
- Test with expired or revoked keys
- Check rate limiting per key

## Phase 3: BOLA / BFLA Testing

### 3.1 Broken Object Level Authorization (BOLA)

OWASP API #1 -- test each data-accessing endpoint:

```bash
# Access resource as user A
curl -s -H "Authorization: Bearer <user_A_token>" <url>/api/orders/123

# Try to access user B's resource with user A's token
curl -s -H "Authorization: Bearer <user_A_token>" <url>/api/orders/456
```

Test on all CRUD operations (GET, PUT/PATCH, DELETE).

### 3.2 Broken Function Level Authorization (BFLA)

OWASP API #5 -- test if regular users can access admin API functions:

```bash
# Admin endpoints with regular user token
curl -s -H "Authorization: Bearer <regular_token>" <url>/api/admin/users
curl -s -H "Authorization: Bearer <regular_token>" -X DELETE <url>/api/users/other_user_id
curl -s -H "Authorization: Bearer <regular_token>" -X POST <url>/api/admin/settings
```

### 3.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| BOLA on sensitive data | High | 7.5 |
| BOLA with write access | Critical | 9.1 |
| BFLA (user -> admin) | Critical | 9.1 |

## Phase 4: Mass Assignment & Data Exposure

### 4.1 Mass Assignment

Test if extra fields in request body are accepted:

```bash
# Try adding fields that shouldn't be user-controllable
curl -s -X PUT -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"name":"test","role":"admin","is_admin":true,"credits":999999}' \
    <url>/api/users/profile
```

### 4.2 Excessive Data Exposure

Check if API responses include more data than needed:
- Internal IDs
- Email addresses of other users
- Password hashes
- Internal system information
- Debug data

```bash
curl -s -H "Authorization: Bearer <token>" <url>/api/users | python3 -m json.tool
```

### 4.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Mass assignment (role escalation) | Critical | 9.1 |
| Mass assignment (balance/credits) | High | 8.1 |
| Excessive PII in responses | Medium | 5.0 |
| Internal IDs exposed | Low | 3.0 |

## Phase 5: Rate Limiting & Resource Consumption

### 5.1 Rate Limit Testing

```bash
# Send 50 rapid requests and check for throttling
for i in $(seq 1 50); do
    echo "Request $i: $(curl -s -o /dev/null -w '%{http_code}' <url>/api/endpoint)"
done
```

Check: Are 429 responses returned? At what threshold?

### 5.2 Resource Consumption

Test for:
- Large payload acceptance (send 10MB+ JSON body)
- Pagination abuse (request page_size=999999)
- Unbound list endpoints (no default limit)
- Expensive operations without throttling

### 5.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| No rate limiting on auth endpoints | High | 7.5 |
| No rate limiting on data endpoints | Medium | 5.3 |
| Unbounded pagination | Medium | 4.5 |
| Large payload acceptance | Low | 3.5 |

## Phase 6: GraphQL-Specific Testing

If GraphQL endpoint was discovered:

### 6.1 Introspection

```bash
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{__schema{types{name fields{name}}}}"}' \
    <url>/graphql
```

If introspection is enabled in production -> Medium finding.

### 6.2 Nested Query Depth

Test for query depth limits:
```graphql
{ user { friends { friends { friends { friends { id } } } } } }
```

No depth limit = potential denial of service.

### 6.3 Batching Attacks

```bash
# Send multiple queries in a single request
curl -s -X POST -H "Content-Type: application/json" \
    -d '[{"query":"{user(id:1){name}}"},{"query":"{user(id:2){name}}"},...]' \
    <url>/graphql
```

Can be used to bypass rate limiting.

### 6.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Introspection enabled in production | Medium | 5.3 |
| No query depth limit | Medium | 5.9 |
| Batch query abuse possible | Medium | 4.5 |
| Field suggestion enabled | Low | 3.5 |

## Phase 7: Input Validation

### 7.1 Type Coercion

Send unexpected types for known parameters:
```bash
# Number field with string
curl -s -X POST -d '{"id":"string_instead_of_number"}' <url>/api/resource

# String field with array
curl -s -X POST -d '{"name":["array","instead"]}' <url>/api/resource

# Boolean field with object
curl -s -X POST -d '{"active":{"$gt":""}}' <url>/api/resource
```

### 7.2 Special Characters

Test with: null bytes, unicode, very long strings, negative numbers, floating point edge cases (NaN, Infinity), empty strings, empty objects/arrays.

## Phase 8: Output

### Terminal Output

**Dev mode:** Explain OWASP API Top 10, what BOLA/BFLA means, why mass assignment happens.

**Pro mode:** Endpoint matrix and findings table.

### VAPT-API.md

```markdown
# VAPT API Security Report

## Target: <url>
## Date: <timestamp>

## API Discovery
| Endpoint | Method | Auth Required | Status |
|----------|--------|--------------|--------|
| ... | ... | ... | ... |

## OpenAPI / Swagger
<spec location and exposure status>

## GraphQL
<introspection results, schema summary>

## BOLA / BFLA
<access control testing results>

## Mass Assignment
<mass assignment testing results>

## Data Exposure
<excessive data in responses>

## Rate Limiting
<rate limit testing results>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt inject <url> -- test API parameters for injections
- /vapt authz <url> -- deeper access control testing
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- API findings weight 12% in Security Posture Score
- Discovered API endpoints expand scope for vapt-inject
- BOLA findings overlap with vapt-authz IDOR testing
