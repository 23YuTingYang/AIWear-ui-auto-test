from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

# 按环境配置创建浏览器驱动，统一处理浏览器初始化细节。
# 当前只实现 Chrome，这样能让上层 fixture 和测试代码不关心具体驱动创建过程。
def create_driver(settings: dict) -> webdriver.Chrome:
    browser = str(settings.get("browser", "chrome")).lower()
    if browser != "chrome":
        raise ValueError(f"当前仅实现 Chrome 驱动，收到: {browser}")

    # 创建 Chrome 浏览器启动参数对象。
    options = ChromeOptions()
    is_headless = settings.get("headless", True)
    if is_headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    # 隐式等待只作为兜底，真正的关键同步仍然依赖页面对象中的显式等待。
    driver.implicitly_wait(min(int(settings.get("implicit_wait", 2)), 10))
    if is_headless:
        width, height = str(settings.get("window_size", "1600,1000")).split(",", 1)
        driver.set_window_size(int(width), int(height))
    else:
        driver.maximize_window()
    return driver


