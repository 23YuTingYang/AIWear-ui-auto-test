from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from utils.yaml_utils import load_yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 定义一个日志缓存字典
# 同一个名称的 logger 只创建一次，避免重复创建 handler，导致日志重复输出。
_LOGGER_CACHE: dict[str, logging.Logger] = {}

# 按名称返回日志实例，并复用当天的文件句柄避免重复创建 handler。
# 每个页面对象通常会以类名取 logger，这样既能区分日志来源，又能避免重复初始化。
def get_logger(name: str) -> logging.Logger:
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    config = load_yaml(PROJECT_ROOT / "config" / "logging.yaml")
    today = datetime.now().strftime("%Y-%m-%d")
    info_path = PROJECT_ROOT / "logs" / "info" / f"{today}.log"
    error_path = PROJECT_ROOT / "logs" / "error" / f"{today}.log"
    # 创建 info 日志目录。
    info_path.parent.mkdir(parents=True, exist_ok=True)
    # 创建 error 日志目录。
    error_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, str(config.get("level", "INFO")).upper(), logging.INFO))
    # 关闭日志向父 logger 传播。 作用是避免一条日志同时被当前 logger 和 root logger 处理，导致控制台或文件里重复输出。
    logger.propagate = False

    # 同名 logger 只绑定一次 handler，避免重复 import 或重复构造对象时出现日志重复输出。
    if not logger.handlers:
        formatter = logging.Formatter(config.get("format", "%(asctime)s | %(levelname)s | %(message)s"))

        info_handler = logging.FileHandler(info_path, encoding="utf-8")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        error_handler = logging.FileHandler(error_path, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(info_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

    _LOGGER_CACHE[name] = logger
    return logger
