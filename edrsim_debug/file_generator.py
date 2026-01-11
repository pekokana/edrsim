# file_generator.py
import os
import time
import random
from pathlib import Path

from core.logger import log_json

class FileGenerator:
    def __init__(self, cfg, burst, logger):
        self.cfg = cfg
        self.burst = burst
        self.logger = logger

        fi = cfg["file_inspection"]
        self.paths = [Path(p) for p in fi["paths"]]
        self.min_kb = fi["min_size_kb"]
        self.max_mb = fi["max_size_mb"]
        self.exts = fi["inspect_extensions"]

    def _pick_extension(self):
        # 拡張子なしも含める
        return random.choice(self.exts + [""])

    def _pick_size(self):
        size_kb = random.choice([
            self.min_kb - 1,
            self.min_kb,
            self.min_kb + 1,
            random.randint(self.min_kb, self.max_mb * 1024),
        ])
        return max(1, size_kb) * 1024

    def generate_once(self):
        base = random.choice(self.paths)
        base.mkdir(parents=True, exist_ok=True)

        ext = self._pick_extension()
        size = self._pick_size()

        fname = f"edr_test_{int(time.time() * 1000)}{ext}"
        fpath = base / fname

        self.burst.hit()

        with open(fpath, "wb") as f:
            f.write(os.urandom(size))

        # 生成ログ（重要）
        log_json(
            self.logger,
            component="edrsim_debug.file_generator",
            event="file_created",
            path=str(fpath),
            size=size,
            ext=ext or "(none)",
        )

    def run(self, count=1, interval=0.1):
        for _ in range(count):
            self.generate_once()
            time.sleep(interval)
