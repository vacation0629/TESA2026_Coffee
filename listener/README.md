# TESA Track 3 — API Listener & Sniffer

Zero-loss traffic capture tool for Phase 1 manual trading and live market monitoring.

## Directory Structure
- `listener/auto_sniffer.py`: mitmproxy / mitmweb sniffer script (captures HTTP GET/POST/PUT/PATCH/DELETE + WebSockets).
- `listener/view_logs.py`: Interactive CLI log inspector and viewer.
- `listener/test_listener.py`: Mock verification test suite.
- `listener/logs/`: Dedicated output directory for append-only `.jsonl` files (gitignored).

## Quick Start

### 1. Run Interactive Sniffer with Visual Dashboard
```powershell
# Optional: Target specific host and port
$env:CAP_HOST = "10.0.1.50"
$env:CAP_PORT = "8000"

# Launch mitmweb with sniffer script
mitmweb -p 8888 -s listener/auto_sniffer.py
```
Open **`http://127.0.0.1:8081`** in your browser to inspect all traffic live.

### 2. Run Headless Sniffer (Console Only)
```powershell
mitmdump -p 8888 -s listener/auto_sniffer.py
```

### 3. View / Prescreen Captured Logs
```powershell
python listener/view_logs.py
```

### 4. Run Mock Verification Tests
```powershell
python listener/test_listener.py
```
