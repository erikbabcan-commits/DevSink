#!/usr/bin/env python3
"""
DevSink Mission Control Web Server, License Engine & Stripe Billing Gateway
Clean, high-performance developer dashboard, automated license key generator, and Stripe Checkout.
Runs on port 3333.
"""

import http.server
import socketserver
import json
import os
import re
import secrets
import shutil
import socket
import sqlite3
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

PORT = int(os.environ.get("DEVSINK_PORT", 3333))
DASHBOARD_DIR = Path(__file__).resolve().parent
DB_PATH = DASHBOARD_DIR / "licenses.db"

# Locate storage base directory
DEFAULT_STORAGE = Path(os.environ.get("DEVSINK_STORAGE", "/home/vorkei/black-hole-cache"))
if not DEFAULT_STORAGE.exists():
    DEFAULT_STORAGE = Path.home() / ".devsink" / "storage"

# Stripe Price IDs
PRICE_PRO_MAC = "price_1UbnvzKy1aN6O8vmSJc4BDUE"  # $19.00 USD one-time
PRICE_CLOUD = "price_1UbnvzKy1aN6O8vm9XVu5otk"    # $5.00 USD / month

def get_stripe_key() -> str:
    env_key = os.environ.get("STRIPE_RESTRICTED_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if env_key:
        return env_key
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

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            customer_email TEXT,
            customer_name TEXT,
            stripe_session_id TEXT UNIQUE,
            stripe_payment_intent TEXT,
            plan_type TEXT NOT NULL,
            amount_paid INTEGER,
            currency TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate_license_key(plan_type="pro") -> str:
    prefix = "DEVSINK-PRO" if plan_type == "pro" else "DEVSINK-CLOUD"
    blocks = [secrets.token_hex(2).upper() for _ in range(4)]
    return f"{prefix}-" + "-".join(blocks)

def get_license_by_session(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT license_key, customer_email, customer_name, plan_type, created_at FROM licenses WHERE stripe_session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "license_key": row[0],
            "customer_email": row[1],
            "customer_name": row[2],
            "plan_type": row[3],
            "created_at": row[4],
        }
    return None

def issue_license_for_session(session_id: str, session_data=None):
    # Check if already issued
    existing = get_license_by_session(session_id)
    if existing:
        return existing

    data = session_data
    if not data:
        key = get_stripe_key()
        if not key:
            return {"error": "Stripe key unavailable for verification"}

        # Fetch session from Stripe
        req = urllib.request.Request(f"https://api.stripe.com/v1/checkout/sessions/{session_id}", headers={
            "Authorization": f"Bearer {key}"
        })
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            return {"error": f"Failed to retrieve session from Stripe: {e}"}

    payment_status = data.get("payment_status")
    if payment_status and payment_status != "paid":
        return {"error": f"Payment is not completed (status: {payment_status})"}

    customer_details = data.get("customer_details") or {}
    email = customer_details.get("email") or data.get("customer_email") or "customer@devsink.local"
    name = customer_details.get("name") or "DevSink Developer"
    amount = data.get("amount_total") or 1900
    currency = data.get("currency") or "usd"
    mode = data.get("mode")
    plan_type = "cloud" if mode == "subscription" else "pro"
    payment_intent = data.get("payment_intent") or data.get("subscription") or ""

    license_key = generate_license_key(plan_type)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO licenses (license_key, customer_email, customer_name, stripe_session_id, stripe_payment_intent, plan_type, amount_paid, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (license_key, email, name, session_id, payment_intent, plan_type, amount, currency))
        conn.commit()
    except Exception:
        pass
    conn.close()

    return {
        "license_key": license_key,
        "customer_email": email,
        "customer_name": name,
        "plan_type": plan_type,
        "amount_paid": amount,
        "currency": currency
    }

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
        "success_url": "http://vorkei.local:3333/success.html?session_id={CHECKOUT_SESSION_ID}",
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

    def do_POST(self):
        # Stripe Webhook Endpoint
        if self.path == "/api/webhook":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            try:
                event = json.loads(post_body.decode("utf-8"))
                event_type = event.get("type")
                if event_type == "checkout.session.completed":
                    session_obj = event.get("data", {}).get("object", {})
                    session_id = session_obj.get("id")
                    if session_id:
                        issue_license_for_session(session_id, session_data=session_obj)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "received"}')
                return
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        return super().do_POST()

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

        # 3. License Info API for Success Page
        if self.path.startswith("/api/license-info?"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            session_id = params.get("session_id", [""])[0]

            if not session_id:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "session_id required"}')
                return

            license_data = issue_license_for_session(session_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(license_data).encode("utf-8"))
            return

        return super().do_GET()

def run():
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadedTCPServer(("0.0.0.0", PORT), DevSinkHandler) as httpd:
        print(f"⚡ DevSink Mission Control, Billing & Webhook UI listening on http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
