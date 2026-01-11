# packet_base.py
class PacketGeneratorBase:
    def send(self, payload_size: int):
        raise NotImplementedError
