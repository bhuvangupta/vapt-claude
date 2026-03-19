#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# VAPT Claude Code Skill Uninstaller
# ============================================================

CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${RED}╔══════════════════════════════════════════╗${NC}"
echo -e "${RED}║   VAPT Claude Code Skill Uninstaller     ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════╝${NC}"
echo ""

# Remove main skill
if [ -d "$SKILLS_DIR/vapt" ]; then
    rm -rf "$SKILLS_DIR/vapt"
    echo -e "${GREEN}[OK] Removed main skill${NC}"
fi

# Remove sub-skills
REMOVED=0
for skill_dir in "$SKILLS_DIR"/vapt-*/; do
    if [ -d "$skill_dir" ]; then
        rm -rf "$skill_dir"
        REMOVED=$((REMOVED + 1))
    fi
done
echo -e "${GREEN}[OK] Removed ${REMOVED} sub-skills${NC}"

# Remove agents
REMOVED=0
for agent_file in "$AGENTS_DIR"/vapt-*.md; do
    if [ -f "$agent_file" ]; then
        rm -f "$agent_file"
        REMOVED=$((REMOVED + 1))
    fi
done
echo -e "${GREEN}[OK] Removed ${REMOVED} agent files${NC}"

echo ""
echo -e "${GREEN}VAPT skill suite uninstalled.${NC}"
echo -e "${BLUE}Note: Security tools (nmap, sqlmap, etc.) were not removed.${NC}"
echo ""
