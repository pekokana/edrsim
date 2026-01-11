# packet_factory.py
from .packet_mock import MockPacketGenerator
from .packet_pcap import PcapPacketGenerator


def create_packet_generator(cfg: dict, logger):
    pkt_cfg = cfg["packet_inspection"]

    # ---- payload inspection 設定 ----
    payload_cfg = pkt_cfg.get("payload_inspection", {})
    enable_payload = payload_cfg.get("enable", False)
    payload_loops = payload_cfg.get("hash_loops", 0) if enable_payload else 0

    mode = pkt_cfg["mode"]

    if mode == "mock":
        return MockPacketGenerator(
            url="http://localhost:8080",
            payload_loops=payload_loops,
            logger=logger
        )

    if mode == "pcap":
        return PcapPacketGenerator(
            dst_ip="127.0.0.1",
            protocol=pkt_cfg["protocols"][0],
            port=pkt_cfg["ports"]["include"][0],
            payload_loops=payload_loops,
        )

    raise ValueError(f"Unknown packet mode: {mode}")
