from __future__ import annotations

import json
import socketserver
import threading
from http.server import BaseHTTPRequestHandler

from llm_observer.config import ObserverConfig
from llm_observer.telemetry import TelemetryClient


class _Handler(BaseHTTPRequestHandler):
    seen_auth: str | None = None
    seen_payload: dict[str, object] | None = None

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        _Handler.seen_auth = self.headers.get("Authorization")
        _Handler.seen_payload = json.loads(body.decode("utf-8"))

        self.send_response(202)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        return


def test_sender_sets_auth_and_payload() -> None:
    with socketserver.TCPServer(("127.0.0.1", 0), _Handler) as httpd:
        port = httpd.server_address[1]
        worker = threading.Thread(target=httpd.handle_request, daemon=True)
        worker.start()

        config = ObserverConfig(
            enabled=True,
            api_key="lok_test.secret",
            endpoint=f"http://127.0.0.1:{port}/v1/events",
            sampling_rate=1.0,
            privacy_mode="hash_only",
            redaction_mode="strict",
            snippets_enabled=False,
            queue_size=8,
            timeout_seconds=1.0,
            retry_budget=0,
            history_size=512,
            savings_factor=0.3,
            savings_min_similarity=0.15,
        )

        client = TelemetryClient(config)
        client.emit({"schema_version": "v1", "provider": "openai"})
        worker.join(timeout=2)
        client.stop()

    assert _Handler.seen_auth == "Bearer lok_test.secret"
    assert _Handler.seen_payload == {"schema_version": "v1", "provider": "openai"}
