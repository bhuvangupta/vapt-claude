# Business Logic Testing

## When Invoked

The user runs `/vapt logic <url>` or this skill is triggered as part of Wave 3 during `/vapt audit`.

## Important Note

Business logic testing is inherently application-specific and mostly manual. This skill provides a structured methodology and specific test scenarios rather than automated scans. The tester must understand the application's business domain to execute these tests effectively.

## Prerequisites

Check for existing context:
- If `VAPT-WAVE2-CONTEXT.md` exists -> use discovered functionality
- If other VAPT output files exist -> use to understand the application's features
- If no context -> crawl the application to identify key workflows

## Phase 1: Application Profiling

### 1.1 Identify Business Functions

Crawl and analyze the application to identify:
- User registration / onboarding flow
- Authentication flows (login, password reset, MFA)
- E-commerce functions (cart, checkout, payment)
- Content management (create, edit, delete)
- Communication features (messaging, comments, sharing)
- Administrative functions
- Export / import features
- Search functionality
- File upload / download
- Subscription / billing

### 1.2 Map Multi-Step Workflows

For each workflow, document:
1. The expected sequence of steps
2. Required inputs at each step
3. Validation rules between steps
4. Expected outcomes

## Phase 2: Workflow Bypass Testing

### 2.1 Step Skipping

For multi-step processes (checkout, registration, wizards):

```bash
# Instead of: Step 1 -> Step 2 -> Step 3 -> Complete
# Try: Step 1 -> Step 3 -> Complete (skip Step 2)
# Try: Directly access Complete step
curl -s -X POST <url>/api/checkout/complete -H "Authorization: Bearer <token>" \
    -d '{"order_id":"123"}'
```

### 2.2 Step Reordering

Can steps be performed out of order? Does the server validate state?

### 2.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Payment bypass via step skipping | Critical | 9.8 |
| Verification bypass (email, phone) | High | 7.5 |
| Non-critical step skippable | Low | 3.5 |

## Phase 3: Race Condition Testing

### 3.1 Time-of-Check-Time-of-Use (TOCTOU)

Send concurrent requests to test for race conditions:

```bash
# Send 10 concurrent requests to the same endpoint
for i in $(seq 1 10); do
    curl -s -X POST <url>/api/transfer \
        -H "Authorization: Bearer <token>" \
        -d '{"amount":100,"to":"other_user"}' &
done
wait
```

Common race condition targets:
- Money transfers / balance deductions
- Coupon / voucher redemption
- Vote / like systems
- Inventory / stock checks
- One-time actions (claim bonus, activate trial)

### 3.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Double-spend / financial race | Critical | 9.1 |
| Coupon reuse via race | High | 7.5 |
| Vote manipulation via race | Medium | 5.0 |

## Phase 4: Numeric & Boundary Testing

### 4.1 Price / Quantity Manipulation

```bash
# Negative quantity
curl -s -X POST <url>/api/cart/add -d '{"product_id":1,"quantity":-1}'

# Zero price
curl -s -X POST <url>/api/cart/add -d '{"product_id":1,"quantity":1,"price":0}'

# Extremely large quantity
curl -s -X POST <url>/api/cart/add -d '{"product_id":1,"quantity":99999999}'

# Decimal abuse
curl -s -X POST <url>/api/transfer -d '{"amount":0.001}'

# Integer overflow
curl -s -X POST <url>/api/cart/add -d '{"quantity":2147483647}'
```

### 4.2 Coupon / Discount Abuse

- Apply same coupon multiple times
- Apply multiple coupons that shouldn't stack
- Use expired coupons
- Tamper with discount percentage in request
- Apply coupon to items outside its scope

### 4.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Negative quantity/price accepted | High | 8.1 |
| Coupon reuse | High | 7.5 |
| Integer overflow causing unexpected behavior | Medium | 5.5 |
| Decimal rounding abuse | Medium | 4.5 |

## Phase 5: Feature Abuse

### 5.1 Email / Notification Abuse

- Can the user trigger unlimited emails (password reset, notifications)?
- Can the user send notifications to arbitrary email addresses?
- Is there rate limiting on notification triggers?

### 5.2 Data Export Abuse

- Can users export more data than they should access?
- Is there rate limiting on export functions?
- Do exports include data of other users?

### 5.3 Search Abuse

- Can search be used for data enumeration?
- Are search results properly filtered by user permissions?
- Can wildcard or regex searches cause performance issues?

### 5.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Email bombing via password reset | Medium | 5.3 |
| Data export exposing other users' data | High | 7.5 |
| Search-based enumeration | Medium | 4.5 |

## Phase 6: File Upload Abuse

### 6.1 File Type Abuse

Test if upload validation can be bypassed:
- Double extension: `file.php.jpg`
- Null byte: `file.php%00.jpg`
- Content-Type mismatch: upload .php with image/jpeg Content-Type
- Polyglot files: valid image that's also valid PHP/HTML
- SVG with embedded scripts

### 6.2 File Size Abuse

- Upload extremely large files to test limits
- Check for decompression bombs (zip bomb, gzip bomb)

### 6.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Executable upload with execution | Critical | 9.8 |
| File type bypass (no execution) | Medium | 5.3 |
| No file size limit | Low | 3.5 |

## Phase 7: Idempotency Testing

### 7.1 Duplicate Actions

Submit the same action multiple times rapidly:
- Create the same resource twice
- Submit the same payment twice
- Perform the same state transition twice

Check if the application properly handles duplicate requests.

### 7.2 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Duplicate payment accepted | Critical | 9.1 |
| Duplicate resource creation (data integrity) | Medium | 5.0 |
| Non-idempotent safe operations | Low | 3.0 |

## Phase 8: Output

### Terminal Output

**Dev mode:** Explain each business logic category, provide real-world case studies, explain why automated scanners miss these.

**Pro mode:** Test results table only.

### VAPT-LOGIC.md

```markdown
# VAPT Business Logic Testing Report

## Target: <url>
## Date: <timestamp>

## Application Profile
<identified business functions and workflows>

## Workflow Bypass
<step skipping and reordering results>

## Race Conditions
<concurrent request test results>

## Numeric / Boundary
<price, quantity, integer manipulation results>

## Feature Abuse
<email, export, search abuse results>

## File Upload
<upload restriction bypass results>

## Idempotency
<duplicate action results>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- Business logic findings weight 5% in Security Posture Score
- Logic flaws often combine with injection or authz findings to create higher-impact chains
- Race condition findings may affect vapt-auth (session/token races)
