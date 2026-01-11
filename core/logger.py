# logger.py
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path
import hashlib
import yaml


def calc_config_hash(cfg: dict) -> str:
    dumped = yaml.dump(cfg, sort_keys=True)
    return hashlib.sha256(dumped.encode()).hexdigest()


class ContextLogger(logging.LoggerAdapter):
    """
    config_hash などの固定コンテキストを自動付与する Logger
    """
    def process(self, msg, kwargs):
        if isinstance(msg, dict):
            msg = {**self.extra, **msg}
        return msg, kwargs

def parse_log_level(level):
    """
    level:
      - "INFO", "DEBUG" などの文字列
      - logging.INFO などの int
    """
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        return getattr(logging, level.upper(), logging.INFO)
    return logging.INFO

def build_file_handler(log_path: Path, rotation_cfg: dict, level: int):
    rtype = rotation_cfg.get("type", "none")

    if rtype == "size":
        handler = RotatingFileHandler(
            log_path,
            maxBytes=rotation_cfg.get("max_bytes", 10 * 1024 * 1024),
            backupCount=rotation_cfg.get("backup_count", 5),
            encoding="utf-8",
        )

    elif rtype == "daily":
        handler = TimedRotatingFileHandler(
            log_path,
            when=rotation_cfg.get("when", "midnight"),
            interval=rotation_cfg.get("interval", 1),
            backupCount=rotation_cfg.get("backup_count", 7),
            encoding="utf-8",
            utc=True,
        )

    elif rtype == "none":
        handler = logging.FileHandler(log_path, encoding="utf-8")

    else:
        raise ValueError(f"Unknown rotation type: {rtype}")

    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler



def setup_component_logger(cfg: dict, component: str):
    log_cfg = cfg.get("logging", {})
    base_dir = Path(log_cfg.get("base_dir", "logs"))
    base_dir.mkdir(parents=True, exist_ok=True)

    default_cfg = log_cfg.get("default", {})
    comp_cfg = log_cfg.get("components", {}).get(component, {})

    level = parse_log_level(comp_cfg.get("level", default_cfg.get("level", "INFO")))

    rotation = default_cfg.get("rotation", {"type": "none"})

    base_file = default_cfg.get("file")
    use_ts = default_cfg.get("timestamp", True)

    edr_name = cfg.get("edr", {}).get("name", "edrsim")

    logger_name = f"{edr_name}.{component}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(parse_log_level(level))
    logger.propagate = False

    if not logger.handlers:
        if base_file:
            if use_ts and rotation.get("type") == "none":
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{edr_name}_{component}_{ts}.log"
            else:
                filename = f"{edr_name}_{component}.log"

            log_path = f"{base_dir}/{filename}"
            handler = build_file_handler(log_path, rotation, level)
        else:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            handler.setFormatter(logging.Formatter("%(message)s"))
        
        logger.addHandler(handler)

    return ContextLogger(
        logger,
        extra={
            "component": component,
            "config_hash": cfg.get("_config_hash"),
        },
    )


def log_json(logger, **fields):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **fields,
    }
    logger.info(json.dumps(record, ensure_ascii=False))