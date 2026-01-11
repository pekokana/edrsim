# packet_pcap.py
from scapy.all import IP, TCP, UDP, send
from .packet_base import PacketGeneratorBase
from .payload_inspector import PayloadInspectorMixin

class PcapPacketGenerator(PacketGeneratorBase, PayloadInspectorMixin):
    def __init__(self, dst_ip, protocol, port, payload_loops):
        self.dst_ip = dst_ip
        self.protocol = protocol
        self.port = port
        self.payload_loops = payload_loops

    def send(self, payload_size: int):
        payload = b"A" * payload_size

        self.inspect_payload(payload, self.payload_loops)

        if self.protocol == "UDP":
            pkt = IP(dst=self.dst_ip) / UDP(dport=self.port) / payload
        else:
            pkt = IP(dst=self.dst_ip) / TCP(dport=self.port) / payload

        send(pkt, verbose=False)
