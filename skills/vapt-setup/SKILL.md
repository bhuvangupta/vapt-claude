# Tool Dependency Checker

## When Invoked

The user runs `/vapt setup`.

## Behavior

Check for all security tools used across the VAPT skill suite, organized by tier. Display installation status and provide install commands for missing tools.

## Tool Registry

### Core (Required)

These tools are needed for basic functionality. Many tests are severely degraded without them.

| Tool | Used By | Check Command | Install (macOS) | Install (Linux) |
|------|---------|--------------|-----------------|-----------------|
| `curl` | All skills | `curl --version` | Pre-installed | `apt install curl` |
| `openssl` | vapt-ssl | `openssl version` | Pre-installed | `apt install openssl` |
| `python3` | Scripts, fallbacks | `python3 --version` | `brew install python3` | `apt install python3` |
| `nmap` | vapt-network, vapt-ssl | `nmap --version` | `brew install nmap` | `apt install nmap` |

### Recommended

Tests will use fallbacks (curl, Python scripts) when these are missing, with reduced coverage.

| Tool | Used By | Check Command | Install (macOS) | Install (Linux) |
|------|---------|--------------|-----------------|-----------------|
| `sqlmap` | vapt-inject | `sqlmap --version` | `pip install sqlmap` | `pip install sqlmap` |
| `nuclei` | vapt-scan | `nuclei --version` | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` | Same |
| `ffuf` | vapt-scan, vapt-api | `ffuf -V` | `go install github.com/ffuf/ffuf/v2@latest` | Same |
| `subfinder` | vapt-recon | `subfinder -version` | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` | Same |
| `nikto` | vapt-scan | `nikto -Version` | `brew install nikto` | `apt install nikto` |
| `testssl.sh` | vapt-ssl | `testssl.sh --version` or `testssl --version` | `brew install testssl` | `git clone https://github.com/drwetter/testssl.sh.git` |

### Optional

Provide additional coverage for specific test areas. Skipped tests are noted in the report.

| Tool | Used By | Check Command | Install (macOS) | Install (Linux) |
|------|---------|--------------|-----------------|-----------------|
| `hydra` | vapt-auth | `hydra -h` | `brew install hydra` | `apt install hydra` |
| `wpscan` | vapt-scan | `wpscan --version` | `gem install wpscan` | `gem install wpscan` |
| `amass` | vapt-recon | `amass -version` | `go install github.com/owasp-amass/amass/v4/...@master` | Same |
| `masscan` | vapt-network | `masscan --version` | `brew install masscan` | `apt install masscan` |
| `dalfox` | vapt-inject | `dalfox version` | `go install github.com/hahwul/dalfox/v2@latest` | Same |
| `feroxbuster` | vapt-scan | `feroxbuster --version` | `brew install feroxbuster` | `apt install feroxbuster` |
| `whatweb` | vapt-recon | `whatweb --version` | `brew install whatweb` | `apt install whatweb` |
| `wafw00f` | vapt-recon | `wafw00f --version` | `pip install wafw00f` | `pip install wafw00f` |
| `sslscan` | vapt-ssl | `sslscan --version` | `brew install sslscan` | `apt install sslscan` |
| `arjun` | vapt-api | `arjun --help` | `pip install arjun` | `pip install arjun` |
| `tplmap` | vapt-inject | `python3 tplmap.py --help` | `git clone https://github.com/epinna/tplmap.git` | Same |
| `commix` | vapt-inject | `commix --version` | `pip install commix` | `pip install commix` |
| `websocat` | vapt-websocket | `websocat --version` | `brew install websocat` | `cargo install websocat` |
| `wscat` | vapt-websocket | `wscat --version` | `npm install -g wscat` | `npm install -g wscat` |
| `kiterunner` | vapt-api | `kr --version` | `go install github.com/assetnote/kiterunner/cmd/kr@latest` | Same |

## Output Format

Display in terminal with color-coded status:

```
VAPT Tool Dependency Check
===========================

Core (required):
  [OK] curl 8.1.2
  [OK] openssl 3.0.9
  [OK] python3 3.11.4
  [OK] nmap 7.94

Recommended:
  [OK] nuclei 3.1.0
  [OK] subfinder 2.6.3
  [!!] sqlmap — NOT FOUND
       Install: pip install sqlmap
  [!!] ffuf — NOT FOUND
       Install: go install github.com/ffuf/ffuf/v2@latest
  [!!] nikto — NOT FOUND
       Install: brew install nikto (macOS) / apt install nikto (Linux)
  [!!] testssl.sh — NOT FOUND
       Install: brew install testssl (macOS)

Optional:
  [OK] hydra 9.5
  [--] wpscan — NOT FOUND
       Install: gem install wpscan
  [--] amass — NOT FOUND
       Install: go install github.com/owasp-amass/amass/v4/...@master
  ...

Summary:
  Core:        4/4 installed
  Recommended: 2/6 installed (4 missing — tests will use fallbacks)
  Optional:    1/12 installed (11 missing — minor coverage reduction)

Python Dependencies:
  [OK] reportlab
  [!!] rich — NOT FOUND
       Install: pip install rich
```

## Execution

For each tool in the registry:
1. Run the check command
2. If found, extract version where possible
3. If not found, show install command for detected OS (check `uname` for macOS vs Linux)

Also check Python dependencies from `requirements.txt`:
```bash
python3 -c "import reportlab" 2>/dev/null && echo "OK" || echo "MISSING"
python3 -c "import rich" 2>/dev/null && echo "OK" || echo "MISSING"
python3 -c "import bs4" 2>/dev/null && echo "OK" || echo "MISSING"
```

## No Output File

This command only outputs to the terminal. It does not create any files.
