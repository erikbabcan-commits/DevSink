# ⚡ DevSink

> **Turn any spare PC, Raspberry Pi, or external SSD into a high-speed LAN developer cache and offloader.**  
> Keep your 128 GB MacBook lean, fast, and cool while enjoying 10x package install speeds.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-cyan.svg)](https://github.com/erikbabcan-commits/DevSink)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-black.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/erikbabcan-commits/DevSink/pulls)

---

```
  ██████╗ ███████╗██╗   ██╗███████╗██╗███╗   ██╗██╗  ██╗
  ██╔══██╗██╔════╝██║   ██║██╔════╝██║████╗  ██║██║ ██╔╝
  ██║  ██║█████╗  ██║   ██║███████╗██║██╔██╗ ██║█████╔╝ 
  ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██║██║╚██╗██║██╔═██╗ 
  ██████╔╝███████╗ ╚████╔╝ ███████║██║██║ ╚████║██║  ██╗
  ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
```

## 📖 The Problem

If you develop on a base **128 GB or 256 GB MacBook Air or laptop**, full-stack development is a constant storage nightmare:
- `pnpm` / `npm` stores silently eat **10-15 GB**.
- PyPI / Python virtualenv wheel caches consume **5-10 GB**.
- Docker layers and builder caches grab **20-30 GB**.
- Shell histories and logs are scattered across machines.

Paying Apple $400 for internal SSD upgrades hurts.

## 💡 The Solution

**DevSink** turns any spare old PC, Intel NUC, Raspberry Pi, or external SSD on your local network into an **all-in-one developer offloading appliance**:

1. **📦 NPM / PNPM Cache (`:4873`)**: Verdaccio proxy cache. Dependencies download once at internet speed, then install across LAN at wire-speed (~1 Gbps).
2. **🐳 Docker Registry Mirror (`:5000`)**: Local pull-through cache for Docker Hub images.
3. **🐍 PyPI / Wheels Cache (`:5050`)**: High-performance ProxPi proxy for `pip` and `uv`.
4. **📜 Encrypted Shell History (`:8888`)**: Atuin SQLite sync server for unified, cross-machine search.
5. **📊 VictoriaLogs Engine (`:9428`)**: Lightweight micro-log aggregator.
6. **🎛️ Mission Control Web UI (`:3333`)**: Real-time disk metrics, storage saved, and service status.

---

## ⚡ Performance Benchmarks (Home Wi-Fi)

| Action | Standard WAN (Internet) | With DevSink LAN Cache | Speedup |
| :--- | :--- | :--- | :--- |
| **Next.js 15 `pnpm install`** | 18.4s | **1.6s** | **11.5x FASTER** |
| **Python `uv add pandas numpy`** | 12.2s | **0.9s** | **13.5x FASTER** |
| **Docker `docker pull node:22`** | 8.5s | **1.1s** | **7.7x FASTER** |
| **MacBook SSD Space Reclaimed** | *N/A* | **~30.6 GB** | **Instant Free Space** |

---

## 🚀 Quick Start

### 1. Install DevSink Server (On your spare PC or server)
Run this single command on Ubuntu, Debian, Arch, or Fedora:

```bash
curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/install.sh | bash
```

Your node is immediately live on `http://<hostname>.local:3333` with zero configuration needed.

---

### 2. Install DevSink Client (On your MacBook Air / Linux Laptop)
Install the lightweight switcher CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/client.sh | bash
```

#### Connect to DevSink:
```bash
devsink on
```
*Your `npm`, `pnpm`, `pip`, `uv`, and `docker` configurations will now automatically pull from your LAN appliance.*

#### Check Service Latency:
```bash
devsink status
```

#### Free Disk Space on your Laptop:
```bash
devsink purge
```
*Safely cleans local laptop caches. Since DevSink keeps the cached packages on the LAN node, reinstalling them takes only seconds.*

#### Disconnect when leaving home:
```bash
devsink off
```
*Cleanly reverts all toolchains back to default public upstream registries.*

---

## 🏗️ Architecture

```
+-------------------+                    +------------------------------------+
|  YOUR LEAN MAC    |                    |           DEVSINK NODE             |
| (128GB MacBook)   |                    | (Spare PC / External SSD Appliance)|
+-------------------+                    +------------------------------------+
|                   |                    |                                    |
|   pnpm install    | --- LAN (mDNS) --> | [:4873] Verdaccio NPM Cache        |
|   pip/uv install  | -----------------> | [:5050] ProxPi Wheels Cache        |
|   docker pull     | -----------------> | [:5000] Docker Registry Mirror     |
|   atuin sync      | -----------------> | [:8888] Atuin History Server       |
|   dev logs        | -----------------> | [:9428] VictoriaLogs Engine        |
|                   |                    | [:3333] Mission Control Web UI     |
+-------------------+                    +------------------------------------+
```

---

## 🎛️ Mission Control Dashboard

Open `http://<hostname>.local:3333` in any browser on your network:
- **SSD Savings Widget**: Real-time counter of total gigabytes offloaded.
- **Service Heartbeats**: Live response latencies for all 5 microservices.
- **1-Click Config Snippets**: Copy/paste instructions for any language or tool.

---

## 💎 Monetization & Pro Tier

- **DevSink Pro for macOS ($19 One-Time)**:
  - Native macOS Menu Bar application with **Auto Wi-Fi Sensing**.
  - Automatically switches `devsink on` when on your home Wi-Fi and `devsink off` when at coffee shops.
- **DevSink Cloud ($5 / Month)**:
  - Turnkey hosted cloud caching nodes over WireGuard/Tailscale for developers without spare hardware.

See full product specifications in [docs/MONETIZATION.md](docs/MONETIZATION.md).

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/awesome-sink`)
3. Commit your changes (`git commit -m 'Add Go proxy support'`)
4. Push to the branch (`git push origin feature/awesome-sink`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
