from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# 读取 YAML 配置文件，供测试数据、环境配置和账号信息统一加载。
def load_yaml(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

