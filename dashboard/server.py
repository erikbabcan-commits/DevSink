#!/usr/bin/env python3
"""
DevSink Mission Control Web Server & Billing Gateway
Clean, high-performance developer dashboard and Stripe Checkout integration.
Runs on port 3333.
"""

import http.server
import socketserver
import json
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

PORT = int(os.environ.get("DEVSINK_PORT", 3333))
DASHBOARD_DIR = Path(__file__).resolve().parent

# Locate storage base directory
DEFAULT_STORAGE = Path(os.environ.get("DEVSINK_STORAGE", "/home/vorkei/black-hole-cache"))
if not DEFAULT_STORAGE.exists():
    DEFAULT_STORAGE = Path.home() / ".devsink" / "storage"

# Stripe Price IDs
PRICE_PRO_MAC = "price_1UbnvzKy1aN6O8vmSJc4BDUE"  # $19.00 USD one-time
PRICE_CLOUD = "price_1UbnvzKy1aN6O8vm9XVu5otk"    # $5.00 USD / month

def get_stripe_key() -> str:
    # 1. Environment variable
    env_key = os.environ.get("STRIPE_RESTRICTED_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if env_key:
        return env_key
    # 2. Local secrets.md (never committed to git)
    secrets_path = Path("/home/vorkei/Documents/secrets.md")
    if secrets_path.exists():
        try:
            content = secrets_path.read_text()
            match = re.search(r"Restricted key\s*-\s*(rk_live_[a-zA-Z0-9]+)", content)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
    return ""

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
        return {"active": True, "code": e.code, "latency_ms": latency}
    except Exception:
        return {"active": False, "code": 0, "latency_ms": -1}

def create_checkout_session(plan: str):
    key = get_stripe_key()
    if not key:
        return {"error": "Stripe API key not configured"}

    if plan == "pro":
        price_id = PRICE_PRO_MAC
        mode = "payment"
    elif plan == "cloud":
        price_id = PRICE_CLOUD
        mode = "subscription"
    else:
        return {"error": "Invalid plan specified"}

    data = {
        "payment_method_types[]": "card",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "mode": mode,
        "success_url": "https://github.com/erikbabcan-commits/DevSink#pro-activation-complete",
        "cancel_url": "http://vorkei.local:3333/#pricing",
    }
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request("https://api.stripe.com/v1/checkout/sessions", data=encoded, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            session_data = json.loads(resp.read().decode())
            return {"url": session_data.get("url")}
    except urllib.error.HTTPError as e:
        return {"error": f"Stripe error: {e.read().decode()}"}
    except Exception as ex:
        return {"error": str(ex)}

class DevSinkHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        # 1. Stats API
        if self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            disk_target = DEFAULT_STORAGE if DEFAULT_STORAGE.exists() else Path.home()
            disk_info = shutil.disk_usage(disk_target)

            npm_size = get_dir_size(DEFAULT_STORAGE / "npm" / "storage")
            docker_size = get_dir_size(DEFAULT_STORAGE / "docker" / "storage")
            pypi_size = get_dir_size(DEFAULT_STORAGE / "pypi" / "storage")
            ghost_log_base = Path("/home/vorkei/ghost-log")
            atuin_size = get_dir_size(ghost_log_base / "history")
            logs_size = get_dir_size(ghost_log_base / "storage")

            total_cache = npm_size + docker_size + pypi_size + atuin_size + logs_size

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

        # 2. Checkout redirect handler
        if self.path.startswith("/api/checkout?"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            plan = params.get("plan", ["pro"])[0]

            res = create_checkout_session(plan)
            if "url" in res:
                self.send_response(303)
                self.send_header("Location", res["url"])
                self.end_headers()
                return
            else:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
                return

        return super().do_GET()

def run():
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadedTCPServer(("0.0.0.0", PORT), DevSinkHandler) as httpd:
        print(f"⚡ DevSink Mission Control & Billing UI listening on http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
