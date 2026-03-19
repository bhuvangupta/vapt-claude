#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# VAPT Claude Code Skill Installer
# Installs the VAPT penetration testing skill for Claude Code
# ============================================================

REPO_URL="https://github.com/bhuvangupta/vapt-claude.git"
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"
INSTALL_DIR="${SKILLS_DIR}/vapt"
TEMP_DIR=$(mktemp -d)

# Detect if running via curl pipe
INTERACTIVE=true
if [ ! -t 0 ]; then
    INTERACTIVE=false
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   VAPT Claude Code Skill Installer       ║${NC}"
    echo -e "${RED}║   Web Application Penetration Testing     ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() { echo -e "${GREEN}[OK] $1${NC}"; }
print_warning() { echo -e "${YELLOW}[!!] $1${NC}"; }
print_error()   { echo -e "${RED}[XX] $1${NC}"; }
print_info()    { echo -e "${BLUE}[>>] $1${NC}"; }

cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

check_security_tools() {
    echo ""
    print_info "Checking security tool dependencies..."
    echo ""

    echo "  Core (required):"
    for tool in curl openssl python3 nmap; do
        if command -v "$tool" &> /dev/null; then
            print_success "  $tool ($($tool --version 2>&1 | head -1))"
        else
            print_error "  $tool — NOT FOUND"
        fi
    done

    echo ""
    echo "  Recommended:"
    for tool in sqlmap nuclei ffuf subfinder nikto; do
        if command -v "$tool" &> /dev/null; then
            print_success "  $tool"
        else
            print_warning "  $tool — NOT FOUND (tests will use fallbacks)"
        fi
    done

    echo ""
    echo "  Optional:"
    for tool in hydra wpscan amass masscan dalfox feroxbuster testssl.sh testssl websocat wscat; do
        if command -v "$tool" &> /dev/null; then
            print_success "  $tool"
        else
            echo -e "  ${BLUE}[--] $tool — NOT FOUND (minor coverage reduction)${NC}"
        fi
    done

    echo ""
    print_info "Run '/vapt setup' in Claude Code for detailed install commands."
    echo ""
}

main() {
    print_header

    # ---- Check Prerequisites ----
    print_info "Checking prerequisites..."

    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed."
        echo "  Install: https://git-scm.com/downloads"
        exit 1
    fi
    print_success "Git found: $(git --version)"

    PYTHON_CMD=""
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if [ -n "$PYTHON_VERSION" ]; then
            MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
            MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
            if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
                PYTHON_CMD="python"
            fi
        fi
    fi

    if [ -z "$PYTHON_CMD" ]; then
        print_error "Python 3.8+ is required but not found."
        echo "  Install: https://www.python.org/downloads/"
        exit 1
    fi
    print_success "Python found: $($PYTHON_CMD --version)"

    if ! command -v claude &> /dev/null; then
        print_warning "Claude Code CLI not found in PATH."
        echo "  This tool requires Claude Code to function."
        echo "  Install: npm install -g @anthropic-ai/claude-code"
        echo ""
        if [ "$INTERACTIVE" = true ]; then
            read -p "Continue installation anyway? (y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            print_info "Non-interactive mode — continuing anyway..."
        fi
    else
        print_success "Claude Code CLI found"
    fi

    # ---- Create Directories ----
    print_info "Creating directories..."

    mkdir -p "$SKILLS_DIR"
    mkdir -p "$AGENTS_DIR"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/scripts"
    mkdir -p "$INSTALL_DIR/templates"

    print_success "Directory structure created"

    # ---- Clone or Copy Repository ----
    print_info "Fetching VAPT skill files..."

    SCRIPT_DIR=""
    if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "bash" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || true
    fi

    if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/vapt/SKILL.md" ]; then
        print_info "Installing from local directory..."
        SOURCE_DIR="$SCRIPT_DIR"
    else
        print_info "Cloning from repository..."
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" || {
            print_error "Failed to clone repository. Check your internet connection."
            exit 1
        }
        SOURCE_DIR="${TEMP_DIR}/repo"
    fi

    # ---- Install Main Skill ----
    print_info "Installing main VAPT skill..."

    cp -r "$SOURCE_DIR/vapt/"* "$INSTALL_DIR/"
    print_success "Main skill installed -> ${INSTALL_DIR}/"

    # ---- Install Sub-Skills ----
    print_info "Installing sub-skills..."

    SKILL_COUNT=0
    for skill_dir in "$SOURCE_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            target_dir="${SKILLS_DIR}/${skill_name}"
            mkdir -p "$target_dir"
            cp -r "$skill_dir"* "$target_dir/"
            SKILL_COUNT=$((SKILL_COUNT + 1))
            print_success "  ${skill_name}"
        fi
    done
    echo "  -> ${SKILL_COUNT} sub-skills installed"

    # ---- Install Agents ----
    print_info "Installing subagents..."

    AGENT_COUNT=0
    for agent_file in "$SOURCE_DIR/agents/"*.md; do
        if [ -f "$agent_file" ]; then
            cp "$agent_file" "$AGENTS_DIR/"
            AGENT_COUNT=$((AGENT_COUNT + 1))
            print_success "  $(basename "$agent_file")"
        fi
    done
    echo "  -> ${AGENT_COUNT} subagents installed"

    # ---- Install Scripts ----
    print_info "Installing utility scripts..."

    if [ -d "$SOURCE_DIR/scripts" ]; then
        cp -r "$SOURCE_DIR/scripts/"* "$INSTALL_DIR/scripts/" 2>/dev/null || true
        chmod +x "$INSTALL_DIR/scripts/"*.py 2>/dev/null || true
        print_success "Scripts installed -> ${INSTALL_DIR}/scripts/"
    fi

    # ---- Install Templates ----
    print_info "Installing report templates..."

    if [ -d "$SOURCE_DIR/templates" ]; then
        cp -r "$SOURCE_DIR/templates/"* "$INSTALL_DIR/templates/" 2>/dev/null || true
        print_success "Templates installed -> ${INSTALL_DIR}/templates/"
    fi

    # ---- Install Python Dependencies ----
    print_info "Installing Python dependencies..."

    if [ -f "$SOURCE_DIR/requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r "$SOURCE_DIR/requirements.txt" --quiet 2>/dev/null && {
            print_success "Python dependencies installed"
        } || {
            print_warning "Some Python dependencies failed to install."
            echo "  Run manually: $PYTHON_CMD -m pip install -r requirements.txt"
            cp "$SOURCE_DIR/requirements.txt" "$INSTALL_DIR/"
        }
    fi

    # ---- Check Security Tools ----
    check_security_tools

    # ---- Verify Installation ----
    print_info "Verifying installation..."

    [ -f "$INSTALL_DIR/SKILL.md" ] && print_success "Main skill file" || print_error "Main skill file missing"
    [ -d "$SKILLS_DIR/vapt-recon" ] && print_success "Sub-skills directory" || print_error "Sub-skills missing"
    [ "$(ls "$AGENTS_DIR"/vapt-*.md 2>/dev/null | wc -l)" -gt 0 ] && print_success "Agent files" || print_error "Agent files missing"
    [ -d "$INSTALL_DIR/scripts" ] && print_success "Utility scripts" || print_error "Scripts missing"

    # ---- Print Summary ----
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        Installation Complete!             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Installed to: ${INSTALL_DIR}"
    echo "  Skills:       ${SKILL_COUNT} sub-skills"
    echo "  Agents:       ${AGENT_COUNT} subagents"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  Open Claude Code and try:"
    echo ""
    echo "    /vapt setup                        # Check tool dependencies"
    echo "    /vapt audit https://example.com     # Full VAPT audit"
    echo "    /vapt recon https://example.com     # Reconnaissance only"
    echo "    /vapt ssl https://example.com       # SSL/TLS analysis"
    echo ""
    echo -e "${BLUE}Available Commands:${NC}"
    echo "    /vapt audit <url>      Full VAPT audit (3 waves)"
    echo "    /vapt recon <url>      Recon & OSINT"
    echo "    /vapt network <url>    Network & port scanning"
    echo "    /vapt ssl <url>        SSL/TLS & crypto analysis"
    echo "    /vapt scan <url>       Web app scanning"
    echo "    /vapt inject <url>     Injection testing"
    echo "    /vapt auth <url>       Authentication & session"
    echo "    /vapt authz <url>      Authorization & access control"
    echo "    /vapt api <url>        API security testing"
    echo "    /vapt graphql <url>    GraphQL security testing"
    echo "    /vapt websocket <url>  WebSocket security testing"
    echo "    /vapt cloud <url>      Cloud misconfiguration"
    echo "    /vapt headers <url>    Security headers & infrastructure"
    echo "    /vapt logic <url>      Business logic testing"
    echo "    /vapt report <url>     Markdown report"
    echo "    /vapt report-pdf <url> PDF report"
    echo "    /vapt setup            Tool dependency check"
    echo ""
    echo -e "${RED}IMPORTANT: Only test targets you have written authorization to test.${NC}"
    echo ""
}

main "$@"
