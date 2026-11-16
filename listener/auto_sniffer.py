from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from mitmproxy import http

# --- Configurable Inputs ---
TARGET_HOST = os.getenv("CAP_HOST", os.getenv("CAP_IP", "")).strip().lower()
TARGET_PORT = os.getenv("CAP_PORT", "").strip()
ALLOWED_TYPES = tuple(
    t.strip().lower()
    for t in os.getenv("CAP_TYPES", "application/json,text/plain,application/x-www-form-urlencoded").split(",")
    if t.strip()
)
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

# Dedicated logs directory
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

print(f"\n==========================================")
print(f" [TESA Track 3] API Listener / Sniffer")
print(f"==========================================")
print(f"  Target Host : {TARGET_HOST or 'ALL (Unrestricted)'}")
print(f"  Target Port : {TARGET_PORT or 'ALL (Unrestricted)'}")
print(f"  Methods     : {', '.join(sorted(ALLOWED_METHODS))} + WebSockets")
print(f"  Log File    : {LOG_FILE}")
print(f"==========================================\n")


def matches_filter(flow: http.HTTPFlow) -> bool:
    """Pre-screens traffic to only keep relevant API payloads and ignore junk."""
    # 1. Skip CORS preflights (OPTIONS) or unhandled methods
    if flow.request.method not in ALLOWED_METHODS:
        return False

    # 2. Port filter
    if TARGET_PORT and str(flow.request.port) != TARGET_PORT:
        return False

    # 3. Host / IP filter
    if TARGET_HOST:
        pretty_host = flow.request.pretty_host.lower()
        peer_ip = (flow.server_conn.peername[0] if flow.server_conn and flow.server_conn.peername else "").lower()
        if TARGET_HOST not in pretty_host and TARGET_HOST != peer_ip:
            return False

    # 4. Skip static web assets (images, fonts, stylesheets, scripts)
    path = flow.request.path.lower()
    ignored_exts = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".css", ".js", ".woff", ".woff2")
    if any(path.endswith(ext) for ext in ignored_exts):
        return False

    # 5. Content-Type check (if response exists)
    if flow.response and ALLOWED_TYPES:
        ctype = flow.response.headers.get("content-type", "").lower()
        if not any(allowed in ctype for allowed in ALLOWED_TYPES):
            return False

    return True


def log_record(record: dict) -> None:
    """Writes record to JSONL with immediate physical disk flush (os.fsync)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def response(flow: http.HTTPFlow) -> None:
    """Triggered on every completed HTTP request/response flow."""
    if not matches_filter(flow):
        return

    req_body = flow.request.get_text(strict=False)
    resp_body = flow.response.get_text(strict=False) if flow.response else ""

    try:
        req_parsed = json.loads(req_body) if req_body else None
    except json.JSONDecodeError:
        req_parsed = req_body

    try:
        resp_parsed = json.loads(resp_body) if resp_body else None
    except json.JSONDecodeError:
        resp_parsed = resp_body

    status = flow.response.status_code if flow.response else 0
    now_ts = datetime.now(timezone.utc).isoformat()

    record = {
        "protocol": "HTTP",
        "ts_utc": now_ts,
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "path": flow.request.path,
        "port": flow.request.port,
        "status_code": status,
        "request_headers": dict(flow.request.headers),
        "request_payload": req_parsed,
        "response_payload": resp_parsed,
    }
    log_record(record)

    # Clean terminal live preview
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{flow.request.method}] {flow.request.path} -> Status {status}")


def websocket_message(flow: http.HTTPFlow) -> None:
    """Triggered on real-time WebSocket / Socket.IO frame messages."""
    assert flow.websocket is not None
    message = flow.websocket.messages[-1]

    if TARGET_HOST and TARGET_HOST not in flow.request.pretty_host.lower():
        return
    if TARGET_PORT and str(flow.request.port) != TARGET_PORT:
        return

    direction = "CLIENT->SERVER" if message.from_client else "SERVER->CLIENT"
    text = message.text

    try:
        parsed = json.loads(text) if text else text
    except json.JSONDecodeError:
        parsed = text

    record = {
        "protocol": "WEBSOCKET",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "url": flow.request.pretty_url,
        "path": flow.request.path,
        "direction": direction,
        "payload": parsed,
    }
    log_record(record)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] [WS:{direction}] {flow.request.path} ({len(text)} chars)")
