# 🚀 DevSink Viral Launch Kit (Hacker News, Reddit, Twitter)

This kit contains tested, community-tailored copy to launch **DevSink** and drive initial GitHub stars and community adoption.

---

## 1. Hacker News (Show HN)

### Title:
`Show HN: DevSink – Turn any spare PC or SSD into a high-speed LAN dev cache and offloader`

### Body:
```text
Hey HN,

I develop on a 128 GB MacBook Air. If you do full-stack web, Python, and Docker builds on a lean laptop, you know the pain: `pnpm`, `pip`, and Docker caches gobble up 30-40 GB in a matter of weeks, leaving your system disk choking.

Rather than buying an overpriced 1TB MacBook or constantly running manual purge commands, I built DevSink.

DevSink turns any spare old PC, Raspberry Pi, or external SSD plugged into a LAN machine into an all-in-one developer offloading appliance.

What it runs:
- Verdaccio (Port 4873): Transparent caching proxy for npm/pnpm. Packages download once at internet speed, then install across LAN at 1,000 Mbps.
- ProxPi (Port 5050): PyPI wheel caching proxy for pip and uv.
- Docker Distribution (Port 5000): Local pull-through registry mirror.
- Atuin (Port 8888): Self-hosted encrypted shell history sync.
- VictoriaLogs (Port 9428): High-speed micro-log aggregator.
- Mission Control Web UI (Port 3333): Real-time metrics showing disk space saved and service latencies.

How client switching works:
We made a POSIX shell CLI (`devsink`):
- `devsink on`: Configures your laptop's npm, pip, uv, and docker to point to `devsink.local` via zero-config mDNS.
- `devsink purge`: Safely nukes all caches on your laptop, freeing 20-30 GB instantly.
- `devsink off`: Cleanly reverts back to official upstream registries when you leave your home Wi-Fi.

Benchmarks on home Wi-Fi:
- `pnpm install` (Next.js 15 project): 18.4s -> 1.6s (11.5x speedup)
- `uv add pandas numpy`: 12.2s -> 0.9s (13.5x speedup)
- SSD space reclaimed on laptop: 30.6 GB

The server installs with a single command on Ubuntu/Debian/Arch:
curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/install.sh | bash

Code is 100% open-source under MIT:
https://github.com/erikbabcan-commits/DevSink

I’d love to hear your feedback on the architecture and what other sinks (e.g. Maven, Go proxy, Homebrew bottle cache) we should add next!
```

---

## 2. Reddit: r/selfhosted

### Title:
`I turned my old dusty PC into a dedicated LAN Developer Appliance (NPM, PyPI, Docker Cache + Shell Sync)`

### Body:
```text
Hey r/selfhosted!

Like many of you, I have an old machine sitting on my local network that I wanted to give real daily utility to. At the same time, my main dev laptop (MacBook Air) was constantly running out of storage due to massive node_modules, global pnpm stores, Docker cache layers, and Python virtualenv wheels.

I packaged together an open-source appliance called **DevSink**.

It bundles:
1. Verdaccio (NPM/PNPM cache proxy)
2. ProxPi (PyPI wheels cache)
3. Docker Registry Mirror
4. Atuin Server (syncs terminal history across all machines securely)
5. VictoriaLogs (fast, lightweight log sink)
6. A lightweight web dashboard on port 3333 showing how much storage your laptop has saved.

The biggest convenience is the client CLI (`devsink`):
- When I'm at home: `devsink on` (points everything to my node over mDNS `hostname.local`)
- When I leave home: `devsink off` (reverts back to official registries)
- When my laptop disk is tight: `devsink purge` (cleans local cache since the remote node holds copies)

Result: My MacBook gained back ~30GB of internal SSD, and fresh package installs take 1-2 seconds over LAN.

GitHub: https://github.com/erikbabcan-commits/DevSink

Hope someone finds it useful for their home lab!
```

---

## 3. Reddit: r/mac

### Title:
`How to survive on a 128GB or 256GB Mac if you are a developer (DevSink)`

### Body:
```text
Apple's storage upgrades are notoriously expensive. If you are coding on a base 128GB or 256GB MacBook, you know that `~/Library/Caches`, Docker images, and global package stores will eat up half your disk.

I built an open-source tool called DevSink that lets you plug any spare external SSD into an old laptop or home mini-PC and offload all package caches (Node, Python, Docker) over your local Wi-Fi.

Your Mac stays completely lean, while `npm install` and `docker pull` run at LAN line-speed (10x faster). When you leave home, a single command (`devsink off`) switches you back to standard internet registries.

Full open-source guide and 1-line script:
https://github.com/erikbabcan-commits/DevSink
```

---

## 4. Twitter / X Launch Thread

```text
1/6 🧵 How I saved my 128 GB MacBook Air without paying Apple's insane storage tax:

I turned an old spare PC + external SSD into "DevSink" — a zero-config LAN developer appliance.

Here is how it works and how you can set it up in 2 minutes 👇

2/6 The problem:
Full-stack development eats disk space alive:
- PNPM / NPM stores: 10GB+
- PyPI / UV wheels: 5GB+
- Docker layers: 20GB+

On a base Mac, your disk is perpetually red.

3/6 The solution: DevSink.
Plug your SSD into any old PC or Raspberry Pi on your home Wi-Fi.
DevSink runs local caching mirrors for NPM, PyPI, and Docker, plus an encrypted shell history server.

4/6 Benchmarks on 1Gbps Wi-Fi:
⚡ Next.js `pnpm install`: 18.4s -> 1.6s
⚡ `uv add pandas`: 12.2s -> 0.9s
💾 30+ GB SSD space reclaimed on laptop

5/6 Switching is effortless:
`devsink on` -> connected to your LAN node
`devsink purge` -> frees gigabytes locally
`devsink off` -> clean revert when at a coffee shop

6/6 100% open source under MIT.
1-Line Installer:
curl -fsSL https://raw.githubusercontent.com/erikbabcan-commits/DevSink/main/install.sh | bash

⭐ Star the repo on GitHub:
https://github.com/erikbabcan-commits/DevSink
```
