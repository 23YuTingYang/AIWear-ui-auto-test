from __future__ import annotations

from datetime import datetime
from pathlib import Path

# 在用例失败时保存截图，便于回溯失败现场并挂载到测试报告。
def save_failure_screenshot(driver, project_root: Path, test_name: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    target_dir = project_root / "screenshots" / "failed" / today
    target_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{test_name}.png"
    file_path = target_dir / file_name
    driver.save_screenshot(str(file_path))
    return str(file_path)
