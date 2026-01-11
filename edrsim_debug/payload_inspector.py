# payload_inspector.py
import hashlib

class PayloadInspectorMixin:
    def inspect_payload(self, payload: bytes, loops: int):
        for _ in range(loops):
            hashlib.sha256(payload).digest()
