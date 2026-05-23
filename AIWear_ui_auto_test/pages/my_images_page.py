from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage


class MyImagesPage(BasePage):
    PATH = "/images"

    # “我的图片”页页面对象。
    # 这是一个复合页面，既承载图片管理主页面，也承载文搜图、图搜图两个子页签的公共能力。

    # 打开“我的图片”页面，并等待主标签区加载完成。
    def open_page(self) -> None:
        self.open(self.PATH)
        self.visible(By.CSS_SELECTOR, ".main-tabs", timeout=10)

    # 按标签名称切换图片管理、文搜图或图搜图子页签。
    def switch_tab(self, tab_name: str) -> None:
        self.click(By.XPATH, f"//button[contains(@class,'main-tab') and contains(normalize-space(.), '{tab_name}')]")

    # 获取当前激活的页签文案，用于断言切换结果, 例如:获取我的图片菜单里面 的我的图片
    def active_tab_text(self) -> str:
        return self.first_visible_text(By.CSS_SELECTOR, ".main-tab.active")

    # 从“我的图片”页面上传素材图片，为后续搜索和编辑场景做准备。
    def upload_image(self, file_path: str) -> None:
        self.send_file_to_input(file_path, (By.CSS_SELECTOR, ".upload-top-btn"))

    # 返回当前页面中的图片卡片元素列表，用于统计和内容断言。
    def image_cards(self) -> list[WebElement]:
        return [
            element
            for element in self.driver.find_elements(By.CSS_SELECTOR, ".grid .item")
            if element.is_displayed()
        ]

    # 提取页面可见图片名称列表，便于校验上传或搜索结果。
    def image_names(self) -> list[str]:
        return self.get_visible_texts(By.CSS_SELECTOR, ".item-name-text")

    # 获取页面头部标题，验证当前主页面是否正确。我的图片
    def title(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".app-header-title")

    # 读取空状态文案，用于断言无搜索结果时的页面反馈。
    def empty_state_text(self) -> str:
        return self.first_visible_text(By.CSS_SELECTOR, ".empty-state-text")

    # 等待空状态文案出现，替代搜索后固定等待。
    def wait_empty_state_text(self, expected_text: str, timeout: int = 10) -> None:
        self._wait(timeout).until(lambda _driver: self.empty_state_text() == expected_text)

    # 等待指定图片名称出现在列表中，确保上传结果已刷新到界面。
    def wait_image_name(self, image_name: str, timeout: int = 10) -> None:
        self._wait(timeout).until(lambda _driver: image_name in self.image_names())

    # 等待图片卡片数量达到下限，避免在列表尚未渲染完成时断言。
    def wait_image_count_at_least(self, count: int, timeout: int = 10) -> None:
        self._wait(timeout).until(lambda _driver: len(self.image_cards()) >= count)
