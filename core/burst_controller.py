# burst_controller.py
import time
import threading
from collections import deque

class BurstController:
    def __init__(self, threshold, window_sec, delay_ms):
        self.threshold = threshold
        self.window_sec = window_sec
        self.delay_ms = delay_ms

        self.events = deque()
        self.lock = threading.Lock()

    def hit(self):
        """
        イベント1回分を記録し、必要なら遅延を入れる
        """
        now = time.time()

        with self.lock:
            self.events.append(now)

            # 古いイベントを捨てる
            while self.events and self.events[0] < now - self.window_sec:
                self.events.popleft()

            if len(self.events) >= self.threshold:
                self._delay()

    def _delay(self):
        """
        FireEyeっぽい「検査遅延」
        """
        time.sleep(self.delay_ms / 1000.0)
