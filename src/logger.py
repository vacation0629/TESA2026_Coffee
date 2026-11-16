from __future__ import annotations
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


class FlightRecorder:
    """Append-only raw JSONL black-box logger + atomic state checkpointer."""

    def __init__(self, log_dir: str = "logs", match_id: str = "default") -> None:
        self.base_dir = Path(log_dir) / match_id
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.base_dir / "raw_events.jsonl"
        self.state_path = self.base_dir / "state_snapshot.json"

    def log_event(
        self,
        event_type: str,
        round_num: int,
        endpoint: str,
        payload: Any,
        status_code: int = 200,
    ) -> None:
        record = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "round": round_num,
            "event_type": event_type,
            "endpoint": endpoint,
            "status_code": status_code,
            "payload": payload,
        }
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def save_state(self, state: dict[str, Any]) -> None:
        tmp_path = self.state_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, self.state_path)

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"history_log": [], "buyer_ceilings": {}, "round_snapshots": {}}
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)


def create_monitored_session(
    recorder: FlightRecorder,
    allowed_ip: str = "",
    allowed_port: int | None = None,
    allowed_types: tuple[str, ...] = ("application/json",),
) -> Any:
    """Creates a requests.Session that filters and logs matching HTTP traffic automatically."""
    if requests is None:
        raise RuntimeError("requests package is required for live HTTP mode.")
    session = requests.Session()

    def _on_response(resp: Any, *args: Any, **kwargs: Any) -> None:
        parsed = urlparse(resp.url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        ctype = resp.headers.get("Content-Type", "").lower()

        if allowed_port is not None and port != allowed_port:
            return
        if allowed_ip:
            try:
                resolved_ip = socket.gethostbyname(parsed.hostname or "")
            except OSError:
                resolved_ip = parsed.hostname or ""
            if allowed_ip not in {resolved_ip, parsed.hostname}:
                return
        if allowed_types and not any(t in ctype for t in allowed_types):
            return

        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        recorder.log_event(
            event_type=f"HTTP_{resp.request.method}",
            round_num=-1,
            endpoint=resp.url,
            payload={
                "port": port,
                "content_type": ctype,
                "request": resp.request.body.decode("utf-8", errors="replace")
                if isinstance(resp.request.body, bytes)
                else resp.request.body,
                "response": body,
            },
            status_code=resp.status_code,
        )

    session.hooks["response"].append(_on_response)
    return session
