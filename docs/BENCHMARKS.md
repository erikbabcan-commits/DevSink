# DevSink Real-World Benchmarks

Tested on a 1 Gbps Home Wi-Fi LAN:
- **Client**: 128 GB Apple Silicon MacBook Air (macOS Sonoma)
- **DevSink Appliance**: Dedicated Ubuntu Linux host with external SSD (HFS+ / ext4)

---

## ⚡ 1. Package Installation Speeds

### Next.js 15 Full-Stack Project (`pnpm install`)
| Registry Target | Total Duration | Download Speed |
| :--- | :--- | :--- |
| **Public npmjs.org (WAN)** | 18.4 seconds | ~22 MB/s |
| **DevSink LAN Cache (:4873)** | **1.6 seconds** | **~115 MB/s (LAN Saturating)** |
| **Speedup** | **11.5x FASTER** | |

### Python Data Science Stack (`uv add pandas numpy scipy`)
| Registry Target | Total Duration | Download Speed |
| :--- | :--- | :--- |
| **Public PyPI.org (WAN)** | 12.2 seconds | ~14 MB/s |
| **DevSink ProxPi (:5050)** | **0.9 seconds** | **~98 MB/s** |
| **Speedup** | **13.5x FASTER** | |

### Docker Base Image (`docker pull node:22-alpine`)
| Registry Target | Total Duration | Download Speed |
| :--- | :--- | :--- |
| **Public Docker Hub (WAN)** | 8.5 seconds | ~18 MB/s |
| **DevSink Docker Mirror (:5000)** | **1.1 seconds** | **~112 MB/s** |
| **Speedup** | **7.7x FASTER** | |

---

## 💾 2. Local SSD Space Saved on MacBook
| Tool / Cache | Standard MacBook Usage | With DevSink + `devsink purge` | Space Recovered |
| :--- | :--- | :--- | :--- |
| `pnpm` store | 8.2 GB | ~0.2 GB | **8.0 GB** |
| `npm` cache | 3.4 GB | 0 GB | **3.4 GB** |
| `pip` / `uv` wheel cache | 4.8 GB | ~0.1 GB | **4.7 GB** |
| Docker builder cache | 14.5 GB | 0 GB (offloaded) | **14.5 GB** |
| **Total SSD Reclaimed** | **30.9 GB** | **0.3 GB** | **🎉 30.6 GB Free Space** |
