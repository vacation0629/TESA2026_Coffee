from __future__ import annotations
import json
import os
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import sniffer logic
import listener.auto_sniffer as sniffer
import listener.view_logs as viewer


class TestListenerMockSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_log_dir = Path("logs/test_logs")
        cls.test_log_dir.mkdir(parents=True, exist_ok=True)
        # Point sniffer to test log dir
        sniffer.LOG_DIR = cls.test_log_dir
        sniffer.LOG_FILE = cls.test_log_dir / "test_capture.jsonl"
        os.environ["LOG_DIR"] = str(cls.test_log_dir)

    @classmethod
    def tearDownClass(cls):
        # Clean test directory
        if cls.test_log_dir.exists():
            shutil.rmtree(cls.test_log_dir)

    def setUp(self):
        # Clear log file before each test
        if sniffer.LOG_FILE.exists():
            sniffer.LOG_FILE.unlink()

    def _create_mock_flow(
        self,
        method: str,
        path: str,
        host: str = "10.0.1.50",
        port: int = 8000,
        req_body: str = "",
        resp_body: str = "",
        status_code: int = 200,
        content_type: str = "application/json",
    ):
        flow = MagicMock()
        flow.request.method = method
        flow.request.path = path
        flow.request.pretty_url = f"http://{host}:{port}{path}"
        flow.request.pretty_host = host
        flow.request.port = port
        flow.request.headers = {"Content-Type": content_type}
        flow.request.get_text.return_value = req_body

        flow.server_conn.peername = (host, port)

        flow.response.status_code = status_code
        flow.response.headers = {"content-type": content_type}
        flow.response.get_text.return_value = resp_body
        return flow

    def test_01_filter_blocks_static_assets(self):
        """Verifies images, css, and js are filtered out."""
        png_flow = self._create_mock_flow("GET", "/static/logo.png", content_type="image/png")
        css_flow = self._create_mock_flow("GET", "/assets/app.css", content_type="text/css")
        js_flow = self._create_mock_flow("GET", "/bundle.js", content_type="application/javascript")

        self.assertFalse(sniffer.matches_filter(png_flow))
        self.assertFalse(sniffer.matches_filter(css_flow))
        self.assertFalse(sniffer.matches_filter(js_flow))

    def test_02_filter_blocks_options_cors(self):
        """Verifies CORS OPTIONS preflight is discarded."""
        options_flow = self._create_mock_flow("OPTIONS", "/api/market/bid")
        self.assertFalse(sniffer.matches_filter(options_flow))

    def test_03_capture_valid_get_board(self):
        """Verifies GET /api/market/board is captured and stored in JSONL."""
        resp_payload = {
            "round": 1,
            "lots": [{"id": "L1", "grade": "A", "sacks": 10}],
            "buyers": [{"id": "B1", "demand": 5}],
        }
        flow = self._create_mock_flow(
            method="GET",
            path="/api/market/board",
            resp_body=json.dumps(resp_payload),
            status_code=200,
        )

        self.assertTrue(sniffer.matches_filter(flow))
        sniffer.response(flow)

        # Verify log file
        self.assertTrue(sniffer.LOG_FILE.exists())
        with open(sniffer.LOG_FILE, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        self.assertEqual(len(lines), 1)
        record = lines[0]
        self.assertEqual(record["protocol"], "HTTP")
        self.assertEqual(record["method"], "GET")
        self.assertEqual(record["path"], "/api/market/board")
        self.assertEqual(record["status_code"], 200)
        self.assertEqual(record["response_payload"]["round"], 1)

    def test_04_capture_valid_post_bid(self):
        """Verifies POST /api/market/bid with JSON body is captured."""
        req_bid = {"lot_id": "L1", "buyer_id": "B1", "sacks": 2, "price_per_kg": 135.50}
        resp_bid = {"success": True, "bid_id": "tx_9981"}

        flow = self._create_mock_flow(
            method="POST",
            path="/api/market/bid",
            req_body=json.dumps(req_bid),
            resp_body=json.dumps(resp_bid),
            status_code=200,
        )

        self.assertTrue(sniffer.matches_filter(flow))
        sniffer.response(flow)

        with open(sniffer.LOG_FILE, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        self.assertEqual(len(lines), 1)
        record = lines[0]
        self.assertEqual(record["method"], "POST")
        self.assertEqual(record["request_payload"]["price_per_kg"], 135.50)
        self.assertEqual(record["response_payload"]["bid_id"], "tx_9981")

    def test_05_capture_websocket_frame(self):
        """Verifies real-time WebSocket / Socket.IO messages are captured."""
        flow = MagicMock()
        flow.request.pretty_url = "ws://10.0.1.50:8000/socket.io"
        flow.request.path = "/socket.io"
        flow.request.pretty_host = "10.0.1.50"
        flow.request.port = 8000

        ws_msg = MagicMock()
        ws_msg.from_client = False
        ws_msg.text = json.dumps({"event": "round_start", "round": 2, "time_left_sec": 300})
        flow.websocket.messages = [ws_msg]

        sniffer.websocket_message(flow)

        with open(sniffer.LOG_FILE, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        self.assertEqual(len(lines), 1)
        record = lines[0]
        self.assertEqual(record["protocol"], "WEBSOCKET")
        self.assertEqual(record["direction"], "SERVER->CLIENT")
        self.assertEqual(record["payload"]["event"], "round_start")

    def test_06_viewer_parses_cleanly(self):
        """Verifies viewer can read the captured log without throwing errors."""
        flow_get = self._create_mock_flow("GET", "/api/market/board", resp_body=json.dumps({"round": 1}))
        flow_post = self._create_mock_flow("POST", "/api/market/bid", req_body=json.dumps({"sacks": 2}), resp_body=json.dumps({"ok": True}))
        sniffer.response(flow_get)
        sniffer.response(flow_post)

        # Run viewer against the test log file
        try:
            sys_argv_bak = viewer.sys.argv
            viewer.sys.argv = ["view_logs.py", str(sniffer.LOG_FILE)]
            viewer.view_latest_log()
        finally:
            viewer.sys.argv = sys_argv_bak


if __name__ == "__main__":
    unittest.main(verbosity=2)
