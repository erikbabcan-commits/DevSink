#!/usr/bin/env python3
"""
DevSink Mission Control Web Server
Lightweight, zero-external-dependency dashboard & telemetry aggregator.
Runs on port 3333.
"""

import http.server
import socketserver
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

PORT = int(os.environ.get("DEVSINK_PORT", 3333))
DASHBOARD_DIR = Path(__file__).resolve().parent

# Locate storage base directory
DEFAULT_STORAGE = Path(os.environ.get("DEVSINK_STORAGE", "/home/vorkei/black-hole-cache"))
if not DEFAULT_STORAGE.exists():
    DEFAULT_STORAGE = Path.home() / ".devsink" / "storage"

SERVICES = [
    {"id": "npm", "name": "NPM / Verdaccio", "port": 4873, "path": "/", "type": "Package Cache"},
    {"id": "docker", "name": "Docker Mirror", "port": 5000, "path": "/v2/", "type": "OCI Container Registry"},
    {"id": "pypi", "name": "PyPI / ProxPi", "port": 5050, "path": "/", "type": "Python Wheels Cache"},
    {"id": "atuin", "name": "Atuin History", "port": 8888, "path": "/", "type": "Encrypted Shell Sync"},
    {"id": "logs", "name": "VictoriaLogs", "port": 9428, "path": "/health", "type": "High-Speed Log Engine"},
]

def get_dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    try:
        # Use fast du if available
        res = subprocess.run(["du", "-sb", str(path)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=2)
        if res.returncode == 0:
            return int(res.stdout.split()[0])
    except Exception:
        pass
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(Path(entry.path))
    except Exception:
        pass
    return total

def format_bytes(b: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.1f} {unit}"
        b /= 1024.0
    return f"{b:.1f} PB"

def check_service(host: str, port: int, path: str):
    url = f"http://127.0.0.1:{port}{path}"
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DevSink-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            latency = int((time.time() - start) * 1000)
            return {"active": True, "code": response.getcode(), "latency_ms": latency}
    except urllib.error.HTTPError as e:
        latency = int((time.time() - start) * 1000)
        # 401 or 404 still means service is actively running and responding
        return {"active": True, "code": e.code, "latency_ms": latency}
    except Exception:
        return {"active": False, "code": 0, "latency_ms": -1}

class DevSinkHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # Disk usage
            disk_target = DEFAULT_STORAGE if DEFAULT_STORAGE.exists() else Path.home()
            disk_info = shutil.disk_usage(disk_target)

            # Sizes
            npm_size = get_dir_size(DEFAULT_STORAGE / "npm" / "storage")
            docker_size = get_dir_size(DEFAULT_STORAGE / "docker" / "storage")
            pypi_size = get_dir_size(DEFAULT_STORAGE / "pypi" / "storage")
            ghost_log_base = Path("/home/vorkei/ghost-log")
            atuin_size = get_dir_size(ghost_log_base / "history")
            logs_size = get_dir_size(ghost_log_base / "storage")

            total_cache = npm_size + docker_size + pypi_size + atuin_size + logs_size

            # Check services
            service_statuses = []
            for s in SERVICES:
                status = check_service("127.0.0.1", s["port"], s["path"])
                service_statuses.append({
                    **s,
                    "active": status["active"],
                    "code": status["code"],
                    "latency_ms": status["latency_ms"]
                })

            data = {
                "hostname": socket.gethostname(),
                "mdns_host": f"{socket.gethostname()}.local",
                "storage_path": str(DEFAULT_STORAGE),
                "disk": {
                    "total": disk_info.total,
                    "total_str": format_bytes(disk_info.total),
                    "used": disk_info.used,
                    "used_str": format_bytes(disk_info.used),
                    "free": disk_info.free,
                    "free_str": format_bytes(disk_info.free),
                    "percent_used": round((disk_info.used / disk_info.total) * 100, 1),
                },
                "cache": {
                    "total_bytes": total_cache,
                    "total_str": format_bytes(total_cache),
                    "npm_bytes": npm_size,
                    "npm_str": format_bytes(npm_size),
                    "docker_bytes": docker_size,
                    "docker_str": format_bytes(docker_size),
                    "pypi_bytes": pypi_size,
                    "pypi_str": format_bytes(pypi_size),
                    "atuin_bytes": atuin_size,
                    "atuin_str": format_bytes(atuin_size),
                    "logs_bytes": logs_size,
                    "logs_str": format_bytes(logs_size),
                },
                "services": service_statuses,
                "timestamp": int(time.time()),
            }

            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        return super().do_GET()

def run():
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadedTCPServer(("0.0.0.0", PORT), DevSinkHandler) as httpd:
        print(f"⚡ DevSink Mission Control UI listening on http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
