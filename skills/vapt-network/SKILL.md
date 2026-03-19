# Network & Port Scanning

## When Invoked

The user runs `/vapt network <url>` or this skill is triggered as part of Wave 2 during `/vapt audit`.

## Phase 1: Port Discovery

### 1.1 Quick Scan (Top Ports)

**If `nmap` is installed:**
```bash
nmap -sT -T4 --top-ports 1000 -oN - <target>
```

**If `rustscan` is installed (fast alternative):**
```bash
rustscan -a <target> --ulimit 5000 -- -sV
```

**If `masscan` is installed (fastest for full range):**
```bash
masscan <target_ip> -p1-65535 --rate=1000
```

**Fallback (Python/netcat):**
```bash
# Check common ports with netcat
for port in 21 22 23 25 53 80 110 111 135 139 143 443 445 993 995 1433 1521 3306 3389 5432 5900 6379 8080 8443 8888 9090 27017; do
    nc -z -w1 <target> $port 2>/dev/null && echo "Port $port: OPEN"
done
```

### 1.2 Service Version Detection

**If `nmap` is installed:**
```bash
nmap -sV -sC -p <open_ports> <target>
```

Flags:
- `-sV` — Probe open ports for service/version info
- `-sC` — Run default NSE scripts

### 1.3 OS Fingerprinting

```bash
nmap -O <target>
```

Note: OS detection requires root/sudo privileges. If not available, infer from service banners and TTL values.

### 1.4 NSE Vulnerability Scripts

Run targeted NSE scripts against discovered services:

```bash
# General vulnerability check
nmap --script vuln -p <open_ports> <target>

# Service-specific scripts
nmap --script http-vuln* -p 80,443,8080 <target>
nmap --script ssh-auth-methods -p 22 <target>
nmap --script mysql-vuln* -p 3306 <target>
nmap --script smb-vuln* -p 445 <target>
```

### 1.5 UDP Scan (Common Services)

```bash
nmap -sU --top-ports 20 <target>
```

Key UDP services to check:
- 53 (DNS)
- 67/68 (DHCP)
- 69 (TFTP)
- 123 (NTP)
- 161/162 (SNMP)
- 500 (IKE/IPSec)
- 514 (Syslog)

## Phase 2: Analysis

### 2.1 Service Risk Assessment

For each discovered service, assess:

| Service | Common Risks |
|---------|-------------|
| FTP (21) | Anonymous login, cleartext creds, known CVEs |
| SSH (22) | Weak algorithms, brute force, old versions |
| Telnet (23) | Cleartext protocol — critical if exposed |
| SMTP (25) | Open relay, user enumeration |
| DNS (53) | Zone transfer, cache poisoning |
| HTTP (80) | Unencrypted web traffic |
| SMB (445) | EternalBlue, null sessions, share enumeration |
| MySQL (3306) | Remote access, default creds |
| PostgreSQL (5432) | Remote access, default creds |
| RDP (3389) | Brute force, BlueKeep |
| Redis (6379) | No auth by default, RCE potential |
| MongoDB (27017) | No auth by default, data exposure |

### 2.2 Unnecessary Exposure

Flag services that shouldn't be publicly accessible:
- Database ports (3306, 5432, 27017, 6379)
- Admin interfaces (management consoles, phpMyAdmin)
- Development services (debug ports, test servers)
- Internal services (SNMP, NFS, SMB)

### 2.3 Scoring

| Finding | Severity | CVSS |
|---------|----------|------|
| Known CVE in service version | Varies | Per CVE |
| Database port publicly accessible | High | 7.5 |
| Telnet enabled | High | 7.4 |
| Redis/MongoDB no auth | Critical | 9.8 |
| FTP anonymous login | Medium | 5.3 |
| Unnecessary ports open | Low | 3.5 |
| SSH weak algorithms | Low | 3.7 |
| Service version disclosure | Info | 0.0 |

## Phase 3: Output

### Terminal Output

Display port scan results as a table with service, version, and risk level.

**Dev mode:** Explain why each open port matters, what an attacker can do with each service, and how to restrict access.

**Pro mode:** Port table with risk flags only.

### VAPT-NETWORK.md

```markdown
# VAPT Network Scan Report

## Target: <target>
## Date: <timestamp>

## Open Ports

| Port | State | Service | Version | Risk |
|------|-------|---------|---------|------|
| 22 | open | ssh | OpenSSH 8.9 | Low |
| 80 | open | http | nginx 1.24 | Info |
| 443 | open | https | nginx 1.24 | Info |
| 3306 | open | mysql | MySQL 8.0.32 | High |
| ... | ... | ... | ... | ... |

## OS Detection
<detected OS or best guess>

## UDP Services
<discovered UDP services>

## NSE Script Results
<vulnerability scan output>

## Findings
<scored findings table>

## Suggested Next Steps
- /vapt scan <url> — scan web services for vulnerabilities
- /vapt inject <url> — test web application for injections
- /vapt auth <url> — test authentication on discovered services
```

## Cross-Skill Integration

- Open ports and services feed into Wave 2 context
- Discovered web services (8080, 8443, etc.) expand scope for vapt-scan
- Database ports inform vapt-inject testing (direct DB access)
- Service versions feed into CVE matching in vapt-scan
