#!/usr/bin/env bash
# ==============================================================================
#  ⚡ DevSink Client 1-Line Installer
# ==============================================================================
#  Install with:
#    curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/client.sh | bash
# ==============================================================================

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "=========================================================="
echo "      ⚡ DEVSINK CLIENT INSTALLER (macOS & Linux)         "
echo "=========================================================="
echo -e "${NC}"

INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_DIR"

BIN_PATH="${INSTALL_DIR}/devsink"
RAW_URL="https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/bin/devsink"

echo -e "⬇️  Downloading DevSink CLI to ${CYAN}${BIN_PATH}${NC}..."
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$RAW_URL" -o "$BIN_PATH"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$BIN_PATH" "$RAW_URL"
else
    echo "Error: curl or wget is required."
    exit 1
fi

chmod +x "$BIN_PATH"

# PATH check
CURRENT_SHELL="$(basename "$SHELL")"
RC_FILE=""
case "$CURRENT_SHELL" in
    zsh)  RC_FILE="$HOME/.zshrc" ;;
    bash) RC_FILE="$HOME/.bashrc" ;;
    *)    RC_FILE="$HOME/.profile" ;;
esac

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}ℹ  Adding ~/.local/bin to your PATH in ${RC_FILE}...${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC_FILE"
    export PATH="$INSTALL_DIR:$PATH"
fi

echo -e "\n${GREEN}${BOLD}✅ DevSink CLI installed successfully!${NC}"
echo -e "Try it right now:\n"
echo -e "  ${BOLD}devsink on${NC}       # Switch local tools to your LAN DevSink node"
echo -e "  ${BOLD}devsink status${NC}   # Check service latency and health"
echo -e "  ${BOLD}devsink off${NC}      # Revert to standard cloud upstreams"
echo ""
