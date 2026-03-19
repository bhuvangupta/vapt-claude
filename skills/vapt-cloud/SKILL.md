# Cloud Misconfiguration Testing

## When Invoked

The user runs `/vapt cloud <url>` for cloud infrastructure security testing.

Detects cloud provider (AWS, Azure, GCP) and tests for common misconfigurations exposed to the public internet.

## Phase 1: Cloud Provider Detection

### 1.1 Infrastructure Fingerprinting

```bash
# Check response headers for cloud indicators
curl -sI <url> | grep -iE 'x-amz|x-goog|x-ms|x-azure|server.*amazon|server.*google|server.*microsoft'

# Check IP ranges
dig +short <domain> | head -1
# Compare resolved IP against known cloud CIDR ranges

# Check for cloud-specific URLs in page source
curl -sL <url> | grep -oiE 'https?://[a-z0-9.-]*(amazonaws\.com|storage\.googleapis\.com|blob\.core\.windows\.net|azurewebsites\.net|cloudfront\.net|appspot\.com)[^"'"'"'\s]*' | sort -u
```

### 1.2 Service Detection

Identify cloud services in use:
- S3/GCS/Azure Blob (object storage)
- CloudFront/Cloud CDN/Azure CDN
- API Gateway
- Lambda/Cloud Functions/Azure Functions
- Cognito/Firebase Auth/Azure AD
- RDS/Cloud SQL/Azure SQL
- ElastiCache/Memorystore/Azure Cache

## Phase 2: Storage Bucket Testing

### 2.1 S3 Bucket Discovery

```bash
# Check for common bucket naming patterns
for prefix in <domain> <domain_no_tld> <company_name> www.<domain> assets.<domain> backup.<domain> dev.<domain> staging.<domain> logs.<domain> media.<domain>; do
    # Check if bucket exists and is listable
    curl -s -o /dev/null -w "%{http_code}" "https://$prefix.s3.amazonaws.com/"
    curl -s -o /dev/null -w "%{http_code}" "https://s3.amazonaws.com/$prefix/"
done
```

### 2.2 Bucket Permission Testing

For discovered buckets:

```bash
# Test list permission (anonymous)
curl -s "https://<bucket>.s3.amazonaws.com/?list-type=2&max-keys=10"

# Test read permission on common files
curl -s -o /dev/null -w "%{http_code}" "https://<bucket>.s3.amazonaws.com/index.html"

# Test write permission (PUT a test file)
curl -s -o /dev/null -w "%{http_code}" -X PUT \
    "https://<bucket>.s3.amazonaws.com/vapt-write-test.txt" \
    -d "VAPT write test - this file should not exist"
```

### 2.3 GCS Bucket Testing

```bash
# Google Cloud Storage
curl -s "https://storage.googleapis.com/<bucket>/"
curl -s "https://storage.googleapis.com/<bucket>/?list-type=2&max-keys=10"
```

### 2.4 Azure Blob Testing

```bash
# Azure Blob Storage
curl -s "https://<account>.blob.core.windows.net/<container>?restype=container&comp=list"
```

### 2.5 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Bucket publicly listable with sensitive data | Critical | 9.1 |
| Bucket publicly writable | Critical | 9.8 |
| Bucket publicly readable (non-sensitive) | Medium | 5.3 |
| Bucket exists but access denied | Info | 0.0 |

## Phase 3: Cloud Metadata & SSRF

### 3.1 Instance Metadata Service (IMDS)

If SSRF vectors exist (from vapt-inject or vapt-api findings), test access to cloud metadata:

**AWS:**
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/user-data
```

**GCP:**
```
http://169.254.169.254/computeMetadata/v1/?recursive=true
(requires header: Metadata-Flavor: Google)
```

**Azure:**
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01
(requires header: Metadata: true)
```

Note: These are only testable if an SSRF vulnerability exists. Do NOT test from the external network -- metadata endpoints are internal only.

### 3.2 IMDSv2 Check

For AWS, check if IMDSv1 (no token required) is still enabled:

```bash
# If you have SSRF, test IMDSv1 (should be disabled)
# IMDSv1: curl http://169.254.169.254/latest/meta-data/
# IMDSv2: requires PUT to get token first
```

### 3.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| SSRF to IMDS leaking credentials | Critical | 9.8 |
| IMDSv1 still enabled | Medium | 5.5 |
| User-data contains secrets | High | 8.1 |

## Phase 4: Cloud Service Misconfigurations

### 4.1 Subdomain Takeover

Check if cloud-hosted subdomains are vulnerable to takeover:

```bash
# Check CNAME records pointing to cloud services
dig +short CNAME <subdomain>

# If CNAME points to a cloud service and returns 404/NoSuchBucket/NXDOMAIN
# -> potential subdomain takeover
```

Cloud services vulnerable to takeover:
- AWS S3 (NoSuchBucket)
- AWS Elastic Beanstalk
- Azure (various services)
- GitHub Pages
- Heroku
- Fastly
- Shopify

### 4.2 Exposed Cloud Consoles

Check for publicly accessible cloud management interfaces:
```bash
# AWS
curl -s -o /dev/null -w "%{http_code}" "<url>/aws-config"
curl -s -o /dev/null -w "%{http_code}" "<url>/.aws/credentials"

# Azure
curl -s -o /dev/null -w "%{http_code}" "<url>/web.config"

# Firebase
curl -s "https://<project>.firebaseio.com/.json"
```

### 4.3 Firebase Misconfiguration

```bash
# Test Firebase Realtime Database access
curl -s "https://<project>.firebaseio.com/.json"

# Test Firestore REST API
curl -s "https://firestore.googleapis.com/v1/projects/<project>/databases/(default)/documents/<collection>"
```

### 4.4 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Subdomain takeover possible | High | 7.5 |
| Exposed AWS credentials file | Critical | 9.8 |
| Firebase database publicly readable | High | 7.5 |
| Firebase database publicly writable | Critical | 9.8 |

## Phase 5: SSL/TLS & CDN Configuration

### 5.1 CDN Bypass

Check if the origin server can be accessed directly (bypassing CDN/WAF):

```bash
# If CloudFront/Cloudflare is detected, look for origin
# Check DNS history, alternative subdomains, certificate SAN
dig +short <domain>
# If behind CDN, try direct IP access
curl -sI -H "Host: <domain>" http://<origin_ip>/
```

### 5.2 Cache Poisoning

For CDN-hosted content:
```bash
# Test cache key manipulation
curl -s -H "X-Forwarded-Host: evil.com" <url>/
curl -s -H "X-Original-URL: /admin" <url>/static/
```

### 5.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| WAF/CDN bypass via direct origin access | High | 7.5 |
| Cache poisoning possible | High | 7.4 |

## Phase 6: Output

### Terminal Output

**Dev mode:** Explain shared responsibility model, why bucket misconfigs happen, how SSRF-to-IMDS attacks work, subdomain takeover mechanics.

**Pro mode:** Cloud asset inventory + findings table.

### VAPT-CLOUD.md

```markdown
# VAPT Cloud Misconfiguration Report

## Target: <url>
## Cloud Provider: <AWS/Azure/GCP/Multi>
## Date: <timestamp>

## Cloud Assets Detected
| Service | Resource | Status |
|---------|----------|--------|
| S3 | <bucket_name> | ... |
| CloudFront | <dist_id> | ... |
| ... | ... | ... |

## Storage Bucket Security
| Bucket | Listable | Readable | Writable |
|--------|----------|----------|----------|
| ... | ... | ... | ... |

## Cloud Metadata / SSRF
<IMDS test results, only if SSRF vector exists>

## Subdomain Takeover
| Subdomain | CNAME | Service | Vulnerable |
|-----------|-------|---------|------------|
| ... | ... | ... | ... |

## Service Misconfigurations
<Firebase, exposed credentials, console access>

## CDN / WAF Bypass
<origin exposure, cache poisoning>

## Findings
<scored findings with CVSS>

## Suggested Next Steps
- /vapt inject <url> -- test for SSRF (required for metadata testing)
- /vapt recon <url> -- discover more cloud assets via DNS
- /vapt report <url> -- compile full report
```

## Cross-Skill Integration

- Cloud findings contribute to network exposure and web app surface categories in Security Posture Score
- SSRF findings from vapt-inject enable deeper cloud metadata testing
- Subdomain discoveries from vapt-recon feed into takeover analysis
