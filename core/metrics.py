# metrics.py
import psutil
import time
import os

from core.logger import log_json

class MetricsLogger:
    def __init__(self, logger, interval_sec=5):
        self.interval_sec = interval_sec
        self.process = psutil.Process(os.getpid())
        self.logger = logger

    def run(self):
        """
        定期的にCPU / メモリをログ出力
        """
        while True:
            cpu = self.process.cpu_percent(interval=1)
            mem = self.process.memory_info().rss / (1024 * 1024)

            log_json(
                self.logger,
                event="process_metrics",
                cpu_percent=round(cpu, 2),
                memory_mb=round(mem, 2),
                pid=self.process.pid,
            )

            time.sleep(self.interval_sec)
