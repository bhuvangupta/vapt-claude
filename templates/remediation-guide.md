# Common Vulnerability Remediation Guide

## SQL Injection (CWE-89)

**Fix:** Use parameterized queries / prepared statements. Never concatenate user input into SQL strings.

**Node.js (pg):**
```javascript
db.query("SELECT * FROM users WHERE id = $1", [userId])
```

**Python (psycopg2):**
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Java (JDBC):**
```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
ps.setInt(1, userId);
```

---

## Cross-Site Scripting -- XSS (CWE-79)

**Fix:** Context-aware output encoding + Content Security Policy. Use framework auto-escaping (React, Vue, Angular handle this by default). For manual encoding, escape &, <, >, ", and ' characters.

**CSP Header:**
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```

---

## Command Injection (CWE-78)

**Fix:** Avoid invoking shell commands with user input. Use language-native APIs or subprocess with argument lists (no shell expansion).

**Python:**
```python
# Safe: use subprocess with list arguments, shell=False
import subprocess
subprocess.run(["ping", "-c", "4", validated_host], shell=False)
```

---

## IDOR / Broken Access Control (CWE-639)

**Fix:** Verify resource ownership on every request. Never trust client-supplied IDs without authorization checks.

```python
@app.get("/api/orders/{order_id}")
def get_order(order_id, current_user=Depends(get_current_user)):
    order = db.get_order(order_id)
    if order.user_id != current_user.id:
        raise HTTPException(403)
    return order
```

---

## Weak SSL/TLS Configuration

**Fix:** Disable old protocols, use strong ciphers only.

**Nginx:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers on;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

---

## Missing Security Headers

**Fix:** Add all recommended headers.

**Nginx:**
```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

---

## JWT Vulnerabilities (CWE-347)

**Fix:** Always validate the algorithm explicitly. Use strong secrets. Verify all claims.

```javascript
// Always enforce the expected algorithm
jwt.verify(token, secret, { algorithms: ['HS256'] })

// For production: prefer RS256 with key pair
jwt.verify(token, publicKey, { algorithms: ['RS256'] })
```

---

## Server-Side Template Injection -- SSTI (CWE-1336)

**Fix:** Never pass user input into template source strings. User input should always be template DATA, not template CODE.

```python
# Safe: user input as data variable, not template source
template = Template("Hello {{ name }}")
template.render(name=user_input)
```

---

## XML External Entity -- XXE (CWE-611)

**Fix:** Disable external entity processing in XML parsers.

**Python (lxml):**
```python
parser = etree.XMLParser(resolve_entities=False, no_network=True)
```

**Java:**
```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

---

## Race Conditions (CWE-362)

**Fix:** Use database-level locking or atomic operations.

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

---

## CORS Misconfiguration (CWE-942)

**Fix:** Never reflect arbitrary origins. Maintain a strict whitelist.

```javascript
const ALLOWED = ['https://app.example.com', 'https://admin.example.com']
const origin = req.headers.origin
if (ALLOWED.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin)
}
```
