from __future__ import annotations
import glob
import json
import os
import sys
from pathlib import Path


def view_latest_log():
    log_dir = os.getenv("LOG_DIR", "logs")
    log_files = sorted(glob.glob(f"{log_dir}/*.jsonl"), key=os.path.getmtime, reverse=True)
    if not log_files:
        print(f"No log files found in '{log_dir}/' directory.")
        return

    target_file = sys.argv[1] if len(sys.argv) > 1 else log_files[0]
    print(f"\n==========================================")
    print(f" Inspecting Log File: {target_file}")
    print(f"==========================================")

    count = 0
    with open(target_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            count += 1
            rec = json.loads(line)
            proto = rec.get("protocol", "HTTP")
            ts = rec.get("ts_utc", "")[:19]

            if proto == "HTTP":
                method = rec.get("method")
                path = rec.get("path")
                status = rec.get("status_code")
                req_data = rec.get("request_payload")
                resp_data = rec.get("response_payload")
                print(f"[{count:03d}] {ts} | {proto:<4} | {method:<6} {path} -> Status {status}")
                if req_data:
                    preview_req = json.dumps(req_data, ensure_ascii=False)
                    print(f"      Req:  {preview_req[:110]}{'...' if len(preview_req) > 110 else ''}")
                if resp_data:
                    preview_resp = json.dumps(resp_data, ensure_ascii=False)
                    print(f"      Resp: {preview_resp[:110]}{'...' if len(preview_resp) > 110 else ''}")
            elif proto == "WEBSOCKET":
                direction = rec.get("direction")
                payload = rec.get("payload")
                print(f"[{count:03d}] {ts} | {proto:<4} | {direction} -> {str(payload)[:100]}")

    print(f"==========================================")
    print(f" Total Captured Events: {count}\n")


if __name__ == "__main__":
    view_latest_log()
