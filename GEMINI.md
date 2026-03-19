# VAPT — Web Application Penetration Testing (Gemini CLI)

This project provides a full-spectrum VAPT (Vulnerability Assessment and Penetration Testing) skill suite. While originally built for Claude Code, the testing methodology and skill files work with Gemini CLI.

## How to Use

Instead of `/vapt <command>`, use natural language:

```
vapt audit https://example.com
vapt recon https://example.com
vapt ssl https://example.com
```

## Tool Mapping

The skill files reference Claude Code tool names. In Gemini CLI, use these equivalents:

| Claude Code Tool | Gemini Equivalent |
|-----------------|-------------------|
| `Bash` | `run_in_terminal` |
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `edit_file` |
| `Glob` | `list_directory` or `run_in_terminal` with `find` |
| `Grep` | `run_in_terminal` with `grep` / `rg` |
| `WebFetch` | `run_in_terminal` with `curl` |
| `Agent` (subagent) | Run tasks sequentially |

## Skill Files

All testing methodology lives in the `skills/` directory. Each `SKILL.md` file contains:
- What to test and how
- Which security tools to use (with fallbacks)
- Output format and findings structure

Read the relevant skill file before starting a test:
- `vapt/SKILL.md` — Main orchestrator and full audit flow
- `skills/vapt-recon/SKILL.md` — Reconnaissance & OSINT
- `skills/vapt-network/SKILL.md` — Network & port scanning
- `skills/vapt-ssl/SKILL.md` — SSL/TLS & cryptography
- `skills/vapt-scan/SKILL.md` — Web application scanning
- `skills/vapt-inject/SKILL.md` — Injection testing (SQLi, XSS, SSTI)
- `skills/vapt-auth/SKILL.md` — Authentication & session testing
- `skills/vapt-authz/SKILL.md` — Authorization & access control
- `skills/vapt-api/SKILL.md` — API security testing
- `skills/vapt-graphql/SKILL.md` — GraphQL security testing
- `skills/vapt-websocket/SKILL.md` — WebSocket security testing
- `skills/vapt-cloud/SKILL.md` — Cloud misconfiguration testing
- `skills/vapt-headers/SKILL.md` — Security headers & infrastructure
- `skills/vapt-logic/SKILL.md` — Business logic testing
- `skills/vapt-report/SKILL.md` — Markdown report generation
- `skills/vapt-report-pdf/SKILL.md` — PDF report generation

## Authorization

Before ANY active testing, you MUST confirm the user has written authorization to test the target. Log authorization to `AUTHORIZATION-LOG.md`.

## Notes

- Subagent-based parallelism (wave architecture) is Claude Code-specific. In Gemini CLI, run the waves sequentially.
- All external tools (nmap, sqlmap, nuclei, etc.) work identically across platforms.
- Output files (VAPT-*.md) are the same regardless of platform.
