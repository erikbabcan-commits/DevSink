# DevSink Architecture & Deep Dive

```
+-------------------------------------------------------------------------+
|                           YOUR LEAN LAPTOP                              |
|                    (128GB MacBook Air / Thin Linux)                     |
|                                                                         |
|   npm / pnpm install      pip / uv install      docker pull             |
+------------+--------------------+---------------------+-----------------+
             |                    |                     |
             | LAN (Zero-Config)  |                     |
             v                    v                     v
+-------------------------------------------------------------------------+
|                             DEVSINK NODE                                |
|          (Old PC / Raspberry Pi / NUC / Dedicated External SSD)         |
|                                                                         |
|  [Port 4873]  Verdaccio NPM/PNPM Cache Proxy                            |
|  [Port 5050]  ProxPi Python Wheels Proxy                                |
|  [Port 5000]  Docker Distribution Registry Mirror                       |
|  [Port 8888]  Atuin Encrypted Shell History Sync Server                 |
|  [Port 9428]  VictoriaLogs High-Speed Micro-Log Engine                  |
|  [Port 3333]  Mission Control Web UI (Disk metrics, service health)     |
|                                                                         |
|  STORAGE POOL:                                                          |
|  /mnt/devsink/storage/                                                  |
|  ├── npm/storage/      (1.2+ GB cached node modules)                    |
|  ├── docker/storage/   (Cached image layers)                            |
|  ├── pypi/storage/     (Pre-compiled fast wheels)                       |
|  ├── history/          (Cross-laptop encrypted terminal SQLite)         |
|  └── logs/             (VictoriaLogs compressed partitions)             |
+-------------------------------------------------------------------------+
```

## Core Design Principles

1. **Zero Laptop Burden**: Your working laptop keeps zero bloated caches. Running `devsink purge` frees dozens of gigabytes locally because any package needed tomorrow will download across LAN at 1,000 Mbps instead of crawling from public internet mirrors.
2. **Deterministic LAN Speeds**: LAN latencies range between 0.2ms and 2ms. Once a package (like Next.js, React, PyTorch, Ubuntu image) is fetched once by anyone on the network, subsequent installs are instantaneous.
3. **No Cloud Dependency**: Operates 100% offline once packages are cached. You can code in the woods on local Wi-Fi without internet access.
4. **Clean 1-Click Rollback**: When stepping outside home Wi-Fi, running `devsink off` cleanly reverts package managers back to official registries with zero corrupted lockfiles or broken environments.
