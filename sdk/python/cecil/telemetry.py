from __future__ import annotations

import json
import queue
import random
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from cecil.config import ObserverConfig
from cecil.logging import get_logger, scrub


@dataclass
class TelemetryCounters:
    sent: int = 0
    dropped: int = 0
    failures: int = 0
    abandoned_on_shutdown: int = 0


class TelemetryClient:
    def __init__(self, config: ObserverConfig) -> None:
        self._config = config
        self._logger = get_logger()
        self._queue: queue.Queue[dict[str, object]] = queue.Queue(maxsize=config.queue_size)
        self._stop = threading.Event()
        self._worker: threading.Thread | None = None
        self.counters = TelemetryCounters()

        if not config.local_only:
            self._worker = threading.Thread(
                target=self._run,
                name="cecil-sdk-telemetry",
                daemon=True,
            )
            self._worker.start()

    def emit(self, event: dict[str, object]) -> None:
        if self._config.local_only:
            return
        if random.random() > self._config.sampling_rate:
            return
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            self.counters.dropped += 1

    def stop(self, timeout: float = 1.0, drain: bool = True) -> None:
        self._stop.set()
        worker = self._worker
        if worker is None:
            return

        deadline = time.monotonic() + max(0.0, timeout)
        if drain:
            while time.monotonic() < deadline:
                if self._queue.empty():
                    break
                time.sleep(0.01)

        remaining = max(0.0, deadline - time.monotonic())
        worker.join(timeout=remaining)
        self._abandon_remaining()
        if worker.is_alive():
            grace = max(0.01, min(0.2, self._config.timeout_seconds + 0.05))
            worker.join(timeout=grace)

    def _abandon_remaining(self) -> None:
        abandoned = 0
        while True:
            try:
                self._queue.get_nowait()
                self._queue.task_done()
                abandoned += 1
            except queue.Empty:
                break

        if abandoned:
            self.counters.abandoned_on_shutdown += abandoned

    def _run(self) -> None:
        while True:
            if self._stop.is_set() and self._queue.empty():
                return

            try:
                event = self._queue.get(timeout=0.05)
            except queue.Empty:
                continue

            self._send_with_retries(event)
            self._queue.task_done()

    def _send_with_retries(self, event: dict[str, object]) -> None:
        attempts = self._config.retry_budget + 1
        for i in range(attempts):
            if self._send_once(event):
                self.counters.sent += 1
                return

            if i < attempts - 1:
                backoff = min(2**i, 8) * 0.1
                time.sleep(backoff)

        self.counters.failures += 1

    def _send_once(self, event: dict[str, object]) -> bool:
        assert self._config.endpoint is not None
        assert self._config.api_key is not None

        payload = json.dumps(event).encode("utf-8")
        request = urllib.request.Request(
            self._config.endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._config.timeout_seconds) as response:
                return bool(200 <= int(response.status) < 300)
        except (urllib.error.URLError, TimeoutError) as exc:
            self._logger.debug(
                "telemetry send failed endpoint=%s err=%s",
                scrub(self._config.endpoint),
                type(exc).__name__,
            )
            return False
