from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from utils.log_utils import get_logger
from utils.wait_utils import build_wait


class BasePage:
    # 所有页面对象的公共父类。
    # 这一层屏蔽 Selenium 的通用操作细节，让业务页面只关注“这个页面能做什么”。

    # 初始化页面对象的公共上下文，统一注入驱动、配置、等待器和日志实例。
    def __init__(self, driver, settings: dict, project_root: Path) -> None:
        self.driver = driver
        self.settings = settings
        self.project_root = project_root
        self.base_url = settings["base_url"].rstrip("/")
        self.timeout = min(int(settings.get("timeout", 10)), 10)
        self.poll_frequency = float(settings.get("poll_frequency", 0.5))
        self.wait = build_wait(driver, self.timeout, self.poll_frequency)
        self.logger = get_logger(self.__class__.__name__)

    # 按需生成新的显式等待对象，支持局部覆盖默认超时时间。
    # 这里对 timeout 做上限控制，避免个别页面等待时间失控，拖慢整套测试。
    def _wait(self, timeout: int | None = None):
        actual_timeout = self.timeout if timeout is None else min(int(timeout), 10)
        return build_wait(self.driver, actual_timeout, self.poll_frequency)

    # 基于基础地址打开指定相对路径页面。
    def open(self, path: str) -> None:
        self.driver.get(self.base_url + path)

    # 等待单个元素出现在 DOM 中并返回元素对象。
    def find(self, by: By, value: str, timeout: int | None = None) -> WebElement:
        return self._wait(timeout).until(EC.presence_of_element_located((by, value)))

    # 等待至少一个元素出现后返回匹配到的全部元素列表。
    def finds(self, by: By, value: str, timeout: int | None = None) -> list[WebElement]:
        self._wait(timeout).until(EC.presence_of_element_located((by, value)))
        return self.driver.find_elements(by, value)

    # 等待元素变为可点击状态，避免点击时机过早导致失败。
    def clickable(self, by: By, value: str, timeout: int | None = None) -> WebElement:
        return self._wait(timeout).until(EC.element_to_be_clickable((by, value)))

    # 等待元素可见并返回，供读取文本或输入前置检查复用。
    def visible(self, by: By, value: str, timeout: int | None = None) -> WebElement:
        return self._wait(timeout).until(EC.visibility_of_element_located((by, value)))
    
    # 对定位到的元素执行标准点击，封装等待与点击两个动作。
    def click(self, by: By, value: str, timeout: int | None = None) -> None:
        self.clickable(by, value, timeout).click()

    # 使用 JavaScript 强制点击元素，处理常规点击受遮挡的场景。
    def js_click(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    # 向输入框写入文本，默认先清空旧值，保持输入行为可重复。
    def type(self, by: By, value: str, text: str, clear: bool = True, timeout: int | None = None) -> None:
        element = self.visible(by, value, timeout)
        if clear:
            element.clear()
        element.send_keys(text)

    # 获取目标元素文本并去掉首尾空白，便于直接做断言。
    def text_of(self, by: By, value: str, timeout: int | None = None) -> str:
        return self.visible(by, value, timeout).text.strip()

    # 解析并返回当前页面路径，屏蔽域名差异，方便做跳转断言。
    # urlparse("http://localhost:3000/images?type=person")
    # scheme: http
    # netloc: localhost:3000
    # path: /images
    # query: type=person
    def current_path(self) -> str:
        return urlparse(self.driver.current_url).path or "/"

    # 判断页面上是否出现指定文本，用于通用提示或标题类断言。
    def has_text(self, text: str, timeout: int | None = None) -> bool:
        try:
            # 在整个页面中，找任意一个“文本里包含指定内容”的元素。
            self._wait(timeout).until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(normalize-space(.), '{text}')]")))
            return True
        except TimeoutException:
            return False

    # 收集一组元素中当前可见的文本列表，便于批量断言页面内容。
    def get_visible_texts(self, by: By, value: str) -> list[str]:
        return [element.text.strip() for element in self.driver.find_elements(by, value) if element.is_displayed()]

    # 返回首个可见且有文本的元素内容，适合断言激活标签或空状态文案。
    def first_visible_text(self, by: By, value: str) -> str:
        for element in self.driver.find_elements(by, value):
            if element.is_displayed():
                text = element.text.strip()
                if text:
                    return text
        raise NoSuchElementException(f"未找到可见文本元素: {value}")

    # 判断元素是否处于可用状态，常用于按钮启用性检查。
    def is_enabled(self, by: By, value: str, timeout: int | None = None) -> bool:
        return self.find(by, value, timeout).is_enabled()

    # 判断元素是否显示在页面上，并将超时视为未显示。
    def is_displayed(self, by: By, value: str, timeout: int | None = None) -> bool:
        try:
            return self.find(by, value, timeout).is_displayed()
        except TimeoutException:
            return False

    # 等待当前 URL 包含指定路径片段，适合异步跳转校验。
    def wait_url_contains(self, path: str, timeout: int | None = None) -> None:
        self._wait(timeout).until(EC.url_contains(path))

    # 等待当前路径精确等于目标值，保证页面已经完成目标跳转。
    def wait_path(self, path: str, timeout: int | None = None) -> None:
        self._wait(timeout).until(lambda driver: urlparse(driver.current_url).path == path)

    # 展开用户头像下拉菜单，为退出登录等头部操作提供前置动作。
    def open_user_dropdown(self) -> None:
        trigger = self.visible(By.CSS_SELECTOR, ".app-header-trigger")
        # 鼠标移动到触发元素上
        ActionChains(self.driver).move_to_element(trigger).pause(0.2).perform()
        # 等待下拉菜单里的菜单项可见。
        self.visible(By.CSS_SELECTOR, ".app-header-dropdown .el-dropdown-menu__item", timeout=5)

    # 从用户下拉菜单中执行退出登录，回到未登录状态。
    def logout(self) -> None:
        self.open_user_dropdown()
        self.click(By.XPATH, "//span[contains(@class,'app-header-logout-item') and contains(normalize-space(.), '退出登录')]")

    # # 按顺序选择图片弹窗中的某一项并确认，适合索引驱动的选图流程。
    # def select_image_from_modal(self, index: int = 1) -> None:
    #     # 定位第 index 个图片按钮
    #     item = self.clickable(
    #         By.XPATH,
    #         f"(//button[contains(@class,'image-select-item')])[{index}]",
    #         timeout=10,
    #     )
    #     # 点击图片按钮
    #     self.js_click(item)
    #     # 点击弹窗里的确认按钮。
    #     self.click(By.CSS_SELECTOR, ".image-select-confirm-btn", timeout=10)
    #     # 等待弹窗关闭
    #     self._wait(10).until(
    #         lambda driver: not any(
    #             element.is_displayed()
    #             # 查找所有图片选择弹窗元素。
    #             for element in driver.find_elements(By.CSS_SELECTOR, ".image-select-dialog")
    #         )
    #     )

    # 按图片标签名称选择弹窗中的指定素材，供业务页面精确选图。
    def select_image_from_modal_by_label(self, label: str) -> None:
        item = self.clickable(
            By.XPATH,
            "//button[contains(@class,'image-select-item')][.//div[contains(@class,'image-select-label') "
            f"and normalize-space(.)='{label}']]",
            timeout=10,
        )
        # 点击目标图片项
        self.js_click(item)
        # 点击图片选择弹窗里的确认按钮。
        self.click(By.CSS_SELECTOR, ".image-select-confirm-btn", timeout=10)
        # 等待弹窗关闭
        self._wait(10).until(
            lambda driver: not any(
                element.is_displayed()
                for element in driver.find_elements(By.CSS_SELECTOR, ".image-select-dialog")
            )
        )

    # 获取当前高亮菜单文案，用于校验左侧导航状态。
    def active_menu_text(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".menu-item.active")

    # 按菜单名称点击左侧导航，驱动不同业务页面之间的跳转。
    def click_menu(self, text: str) -> None:
        self.click(By.XPATH, f"//nav[contains(@class,'menu')]//a[contains(@class,'menu-item')]//span[normalize-space(.)='{text}']")

    # 向可用文件输入框注入文件路径，兼容隐藏上传控件的实现方式。
    # 由于前端上传控件常会把 input[type=file] 隐藏在按钮背后，这里直接对真实 input 注入路径，
    # 让上传逻辑对不同页面复用同一套实现。
    def send_file_to_input(self, file_path: str, trigger: tuple[By, str] | None = None) -> None:
        if trigger:
            trigger_el = self.clickable(*trigger)
            self.js_click(trigger_el)

        selector = "input[type='file']:not([disabled])"   #找到所有 type=file 的 input,但不要 disabled 的。
        last_error: Exception | None = None # 准备记录最后一次异常

        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)  #查找所有匹配的文件 input
        for element in elements:
            try:
                self.driver.execute_script(
                    "arguments[0].style.display='block'; arguments[0].style.visibility='visible';",
                    element,
                )
                element.send_keys(file_path)
                return
            except Exception as exc:
                last_error = exc

        raise NoSuchElementException(f"未找到可用文件输入框: {last_error}")
