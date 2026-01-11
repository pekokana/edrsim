# main.py
import yaml
import threading
import time
import hashlib

from core.logger import setup_component_logger, log_json
from core.burst_controller import BurstController
from core.metrics import MetricsLogger
from .file_generator import FileGenerator
from .packet_factory import create_packet_generator

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()

    cfg_hash = hashlib.sha256(
        yaml.dump(cfg, sort_keys=True).encode("utf-8")
    ).hexdigest()

    # cfg に一度だけ埋め込む
    cfg["_config_hash"] = cfg_hash

    logger = setup_component_logger(cfg, "debug")


    # 起動ログ（あとで検証が超楽になる）
    log_json(
        logger,
        component="edrsim_debug",
        event="startup",
        file_inspection=cfg["file_inspection"]["enable"],
        packet_inspection=cfg["packet_inspection"]["enable"],
    )

    burst_cfg = cfg["file_inspection"]["burst_control"]
    burst = BurstController(
        threshold=burst_cfg["threshold"],
        window_sec=burst_cfg["window_sec"],
        delay_ms=burst_cfg["delay_ms"]
    )

    # メトリクス
    metrics_logger = setup_component_logger(cfg, "metrics.debug")
    metrics = MetricsLogger(metrics_logger, interval_sec=5)
    threading.Thread(target=metrics.run, daemon=True, name="debug-metrics").start()

    # ジェネレータ
    file_gen = FileGenerator(cfg, burst, logger)
    pkt_gen = create_packet_generator(cfg, logger)

    def file_loop():
        while True:
            file_gen.run(count=5, interval=0.05)

    def packet_loop():
        while True:
            burst.hit()
            pkt_gen.send(payload_size=512)
            time.sleep(0.02)

    threading.Thread(target=file_loop, daemon=True).start()
    threading.Thread(target=packet_loop, daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
