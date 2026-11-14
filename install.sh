#!/usr/bin/env bash
# ==============================================================================
#  ⚡ DevSink Universal Server Installer
# ==============================================================================
#  Turns any Linux PC, NUC, Raspberry Pi, or external SSD into a dedicated
#  LAN Developer Appliance with NPM, Docker, PyPI caching, and encrypted history.
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/install.sh | bash
# ==============================================================================

set -e

VERSION="1.0.0"
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
  ██████╗ ███████╗██╗   ██╗███████╗██╗███╗   ██╗██╗  ██╗
  ██╔══██╗██╔════╝██║   ██║██╔════╝██║████╗  ██║██║ ██╔╝
  ██║  ██║█████╗  ██║   ██║███████╗██║██╔██╗ ██║█████╔╝ 
  ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██║██║╚██╗██║██╔═██╗ 
  ██████╔╝███████╗ ╚████╔╝ ███████║██║██║ ╚████║██║  ██╗
  ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
EOF
echo -e "   Turn Any PC / SSD into a High-Speed LAN Developer Appliance (v${VERSION})"
echo -e "${NC}"

# Detect OS & Package Manager
OS_TYPE="$(uname -s)"
if [ "$OS_TYPE" != "Linux" ]; then
    echo -e "${RED}Error:${NC} DevSink Server runs on Linux (Ubuntu, Debian, Arch, Fedora, Raspberry Pi OS)."
    echo "For client-side Mac installation, use: curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/client.sh | bash"
    exit 1
fi

# Detect Hostname & IP
HOSTNAME="$(hostname)"
MDNS_NAME="${HOSTNAME}.local"
PRIMARY_IP="$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}' || hostname -I | awk '{print $1}')"

echo -e "📍 Detected Node Host: ${BOLD}${MDNS_NAME}${NC} (IP: ${CYAN}${PRIMARY_IP}${NC})"

# Storage Directory Resolution
TARGET_STORAGE="${DEVSINK_STORAGE}"
if [ -z "$TARGET_STORAGE" ]; then
    # Check if existing black-hole-cache exists
    if [ -d "/home/$USER/black-hole-cache" ]; then
        TARGET_STORAGE="/home/$USER/black-hole-cache"
    else
        TARGET_STORAGE="$HOME/.devsink/storage"
    fi
fi

echo -e "💾 Target Cache Storage: ${BOLD}${TARGET_STORAGE}${NC}"
mkdir -p "$TARGET_STORAGE"/{npm/storage,docker/storage,pypi/storage,history,logs}

# Clone or Update DevSink Repository
INSTALL_DIR="$HOME/.devsink/core"
mkdir -p "$HOME/.devsink"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing DevSink installation..."
    cd "$INSTALL_DIR" && git pull --quiet || true
else
    echo "Fetching DevSink core repository..."
    if command -v git >/dev/null 2>&1; then
        git clone --quiet https://github.com/erikbabcan-commits/DevSink.git "$INSTALL_DIR" || {
            mkdir -p "$INSTALL_DIR"
            cp -r /home/vorkei/projects/devsink/* "$INSTALL_DIR"/ 2>/dev/null || true
        }
    fi
fi

# Install Client CLI locally
mkdir -p "$HOME/.local/bin"
cp "$INSTALL_DIR/bin/devsink" "$HOME/.local/bin/devsink" 2>/dev/null || true
chmod +x "$HOME/.local/bin/devsink" 2>/dev/null || true

# Setup Systemd User Service for Dashboard
mkdir -p "$HOME/.config/systemd/user"
cat << EOF > "$HOME/.config/systemd/user/devsink-dashboard.service"
[Unit]
Description=DevSink Mission Control Web Dashboard (:3333)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_DIR/dashboard/server.py
WorkingDirectory=$INSTALL_DIR/dashboard
Restart=always
RestartSec=3s
Environment=DEVSINK_PORT=3333
Environment=DEVSINK_STORAGE=$TARGET_STORAGE

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable devsink-dashboard.service 2>/dev/null || true
systemctl --user restart devsink-dashboard.service 2>/dev/null || true

# Avahi check (mDNS)
if ! command -v avahi-daemon >/dev/null 2>&1; then
    echo -e "${YELLOW}Notice:${NC} For zero-config ${MDNS_NAME} resolution, install avahi-daemon:"
    echo "  sudo apt update && sudo apt install -y avahi-daemon"
fi

echo ""
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✨ DevSink Server is Installed & Running!${NC}"
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  🎛️  ${BOLD}Mission Control Dashboard:${NC} ${CYAN}http://${MDNS_NAME}:3333${NC} (or http://${PRIMARY_IP}:3333)"
echo -e "  📦  ${BOLD}NPM / PNPM Cache:${NC}          ${CYAN}http://${MDNS_NAME}:4873${NC}"
echo -e "  🐳  ${BOLD}Docker Mirror Registry:${NC}    ${CYAN}http://${MDNS_NAME}:5000${NC}"
echo -e "  🐍  ${BOLD}PyPI Wheel Proxy:${NC}          ${CYAN}http://${MDNS_NAME}:5050${NC}"
echo -e "  📜  ${BOLD}Atuin Shell Sync:${NC}          ${CYAN}http://${MDNS_NAME}:8888${NC}"
echo -e "  📊  ${BOLD}VictoriaLogs Engine:${NC}       ${CYAN}http://${MDNS_NAME}:9428${NC}"
echo ""
echo -e "  💻  ${BOLD}To connect your MacBook Air or Linux Laptop, run:${NC}"
echo -e "      ${YELLOW}curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/client.sh | bash${NC}"
echo -e "      ${YELLOW}devsink on${NC}"
echo ""
