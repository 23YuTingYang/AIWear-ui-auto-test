from __future__ import annotations

from selenium.webdriver.support.ui import WebDriverWait

# 创建统一的显式等待对象，避免页面元素加载时序导致测试不稳定。
def build_wait(driver, timeout: int, poll_frequency: float = 0.5) -> WebDriverWait:
    return WebDriverWait(driver, timeout=timeout, poll_frequency=poll_frequency)

