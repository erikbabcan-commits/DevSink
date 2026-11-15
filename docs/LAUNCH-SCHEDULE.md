# 📅 DevSink Viral Launch Playbook & Timing Schedule

To maximize initial traction, stars, and early sales, follow this synchronized launch calendar.

---

## ⏰ Optimal Timing Window
* **Best Days**: **Tuesday or Wednesday** (Avoid Friday–Sunday when developer traffic dips by 40%).
* **Best Hours**: **08:00 AM – 09:30 AM EST** (14:00 – 15:30 CET / Bratislava time).
  * This catches the US East Coast starting their workday and the European developer community in their afternoon peak.

---

## 🚀 Step-by-Step Launch Sequence

```
[08:00 AM EST] → Publish Hacker News "Show HN"
[08:15 AM EST] → Post First Comment on HN (Technical deep-dive & benchmarks)
[08:30 AM EST] → Post on Reddit r/selfhosted
[09:00 AM EST] → Post on Reddit r/mac (Focus: 128GB MacBook Air storage survival)
[09:30 AM EST] → Publish Twitter / X 6-tweet Thread
[10:00 AM EST] → Monitor & Reply to every comment within 5 minutes
```

---

## 1. Hacker News Show HN Execution

* **URL to submit**: `https://github.com/erikbabcan-commits/DevSink`
* **Title**:
  ```text
  Show HN: DevSink – Turn any spare PC or SSD into a high-speed LAN dev cache
  ```
* **First Author Comment (Post immediately within 60 seconds of submission)**:
  ```text
  Hey HN, author here.

  Like many developers on 128 GB / 256 GB MacBooks, I was constantly running `docker system prune` and clearing `pnpm` global stores to avoid choking my internal SSD. 

  Rather than paying Apple $400 for an SSD upgrade, I built DevSink. It packages:
  - Verdaccio (Port 4873): transparent npm/pnpm caching proxy
  - ProxPi (Port 5050): PyPI wheel caching proxy for pip & uv
  - Docker Registry Mirror (Port 5000): local pull-through cache for Docker Hub
  - Atuin (Port 8888): self-hosted encrypted shell history sync
  - VictoriaLogs (Port 9428): compressed fast micro-log sink
  - Web UI (Port 3333): real-time disk savings telemetry

  The client switcher CLI (`devsink on` / `devsink off`) uses zero-config mDNS (`hostname.local`). Once cached, `pnpm install` drops from 18.4s to 1.6s, completely saturating home Wi-Fi line speed.

  The core appliance is 100% open source (MIT). Happy to answer questions about architecture, cache invalidation, or storage pruning!
  ```

---

## 2. Reddit r/selfhosted Execution

* **Subreddit**: `r/selfhosted`
* **Flair**: `Showcase`
* **Title**:
  ```text
  I turned an old dusty PC + SSD into a dedicated LAN Developer Cache appliance (DevSink)
  ```
* **Post Content**: Use the drafted text from `docs/LAUNCH-KIT.md`.
* **Pro-tip**: Highlight that it works on Raspberry Pi 4/5, Intel NUCs, or any old Linux box.

---

## 3. Reddit r/mac Execution

* **Subreddit**: `r/mac`
* **Title**:
  ```text
  How to survive on a 128GB or 256GB Mac if you are a developer (DevSink)
  ```
* **Angle**: Emphasize how much disk space is saved (~30 GB) without paying Apple's SSD prices.

---

## 4. First-Hour Comment Defense Strategy

Be prepared to answer these common technical objections:
1. **"Why not just use Docker on the Mac?"**
   * *Answer*: Docker Desktop on Mac consumes 15-25 GB in `Docker.raw` virtual disk and eats CPU/RAM. Offloading the registry mirror to an external machine keeps the Mac completely silent and cool.
2. **"What happens when I travel without my home network?"**
   * *Answer*: Run `devsink off` (or the macOS Menu Bar app detects SSID switch automatically) and all package managers immediately fall back to standard public cloud upstreams.
3. **"How do you handle cache overflow on the appliance?"**
   * *Answer*: Built-in `prune-cache.sh` runs LRU eviction when disk usage exceeds 80%.
