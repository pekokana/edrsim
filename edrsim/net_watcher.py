import time
import hashlib
import random
from collections import deque
import threading

from core.logger import setup_component_logger, log_json
from core.metrics import MetricsLogger

class PacketWatcher:

    def __init__(self, cfg, logger):
        self.cfg = cfg
        # ログ設定
        self.logger = logger

        pi = cfg["packet_inspection"]
        self.payload_cfg = pi["payload_inspection"]

        bc = pi["burst_control"]
        self.burst_threshold = bc["threshold"]
        self.burst_window = bc["window_sec"]
        self.burst_delay = bc["delay_ms"] / 1000

        self.event_times = deque()

    def inspect_packet(self, payload: bytes):
        now = time.time()
        self.event_times.append(now)

        while self.event_times and now - self.event_times[0] > self.burst_window:
            self.event_times.popleft()

        if len(self.event_times) >= self.burst_threshold:
            time.sleep(self.burst_delay)

        if not self.payload_cfg["enable"]:
            return

        if len(payload) < self.payload_cfg["min_payload_size"]:
            return

        start = time.time()
        for _ in range(self.payload_cfg["hash_loops"]):
            hashlib.md5(payload).hexdigest()

        elapsed = (time.time() - start) * 1000

        log_json(
            self.logger,
            event="packet_inspected",
            payload_size=len(payload),
            inspect_ms=round(elapsed, 2)
        )

    def run_mock(self):
        # packet_watcher プロセス専用 metrics logger
        metrics_logger = setup_component_logger(self.cfg, "metrics.packet")
        metrics = MetricsLogger(metrics_logger, interval_sec=5)

        threading.Thread(
            target=metrics.run,
            daemon=True,
            name="packet-metrics"
        ).start()

        log_json(
            self.logger,
            event="packet_watcher_start",
            mode="mock"
        )

        while True:
            payload = str(random.random()).encode()
            self.inspect_packet(payload)
            time.sleep(0.005)
