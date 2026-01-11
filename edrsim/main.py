from multiprocessing import Process
import yaml
import hashlib
import threading

from watchdog.observers import Observer
from core.config import load_config
from .file_watcher import FileWatcher
from .net_watcher import PacketWatcher
from core.logger import calc_config_hash
from core.logger import setup_component_logger, log_json
from core.metrics import MetricsLogger

if __name__ == "__main__":
    cfg = load_config("config.yaml")

    # cfg に一度だけ埋め込む
    cfg["_config_hash"] = calc_config_hash(cfg)

    logger = setup_component_logger(cfg, "main")
    # 起動ログ
    log_json(
        logger,
        component="edrsim",
        event="startup",
        edr=cfg["edr"],
        file_inspection=cfg["file_inspection"],
        packet_inspection=cfg["packet_inspection"],
    )

    main_metrics_logger = setup_component_logger(cfg, "metrics.main")
    metrics = MetricsLogger(main_metrics_logger, interval_sec=5)

    threading.Thread(
        target=metrics.run,
        daemon=True,
        name="metrics-thread"
    ).start()

    processes = []

    if cfg["file_inspection"]["enable"]:
        fw_logger = setup_component_logger(cfg, "file_watcher")
        fw = FileWatcher(cfg, fw_logger)
        obs = Observer()
        for path in cfg["file_inspection"]["paths"]:
            obs.schedule(
                fw,
                path,
                recursive=cfg["file_inspection"].get("recursive", True)
            )
        obs.start()

    if cfg["packet_inspection"]["enable"]:
        pw_logger = setup_component_logger(cfg, "packet_watcher")
        pw = PacketWatcher(cfg, pw_logger)
        p = Process(target=pw.run_mock)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
