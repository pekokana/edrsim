import os
import random
import time

from core.logger import get_logger

class PacketGenerator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = get_logger("packet")

        pi = cfg["packet_inspection"]
        payload_cfg = pi["payload_inspection"]

        self.min_size = payload_cfg["min_payload_size"]
        self.max_size = payload_cfg.get(
            "max_payload_size", self.min_size * 2
        )

    def send(self, payload_size: int | None = None):
        if payload_size is None:
            payload_size = random.randint(self.min_size, self.max_size)

        payload = os.urandom(payload_size)

        # ここで「送信したことにする」
        # 実装を差し替えやすい構造
        self.logger.info(
            "packet_sent size=%d",
            payload_size
        )

        # EDR検知を想定した微小遅延
        time.sleep(0.001)
