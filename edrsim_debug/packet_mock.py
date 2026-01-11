# packet_mock.py
import requests
from .packet_base import PacketGeneratorBase
from .payload_inspector import PayloadInspectorMixin
from core.logger import log_json

class MockPacketGenerator(PacketGeneratorBase, PayloadInspectorMixin):
    def __init__(self, url, payload_loops, logger):
        self.url = url
        self.payload_loops = payload_loops
        self.logger = logger

    def send(self, payload_size: int):
        payload = b"A" * payload_size

        self.inspect_payload(payload, self.payload_loops)

        log_json(
            self.logger,
            component="edrsim_debug.packet_mock",
            event="packet_send",
            payload_size=payload_size,
            mode="mock",
        )

        try:
            requests.post(self.url, data=payload, timeout=1)
        except Exception:
            pass
