import time
import os
import hashlib
from collections import deque
from watchdog.events import FileSystemEventHandler
from core.logger import setup_component_logger, log_json

class FileWatcher(FileSystemEventHandler):

    def __init__(self, cfg, logger):
        self.cfg = cfg

        # ログ設定
        # self.logger = setup_component_logger(self.cfg, "file_watcher")
        self.logger = logger

        fi = cfg["file_inspection"]
        self.min_size = fi["min_size_kb"] * 1024
        self.max_size = fi["max_size_mb"] * 1024 * 1024
        self.extensions = set(fi["inspect_extensions"])

        bc = fi["burst_control"]
        self.burst_threshold = bc["threshold"]
        self.burst_window = bc["window_sec"]
        self.burst_delay = bc["delay_ms"] / 1000

        self.light_loops = fi["light_scan_hash_loops"]
        self.full_loops = fi["full_scan_hash_loops"]

        self.event_times = deque()

    def on_modified(self, event):
        if not event.is_directory:
            self.handle(event.src_path)

    def handle(self, path):
        now = time.time()
        self.event_times.append(now)

        while self.event_times and now - self.event_times[0] > self.burst_window:
            self.event_times.popleft()

        if len(self.event_times) >= self.burst_threshold:
            time.sleep(self.burst_delay)

        try:
            size = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lower()
        except Exception:
            return

        if size < self.min_size or ext not in self.extensions:
            return

        self.inspect(path, size)

    def inspect(self, path, size):
        loops = self.full_loops if size > self.max_size else self.light_loops

        start = time.time()
        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception:
            return

        for _ in range(loops):
            hashlib.sha256(data).hexdigest()

        elapsed = (time.time() - start) * 1000

        log_json(
            self.logger,
            component="file_inspection",
            event="inspect",
            path=path,
            size=size,
            hash_loops=loops,
            inspect_ms=round(elapsed, 2)
        )
