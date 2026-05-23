from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.my_images_page import MyImagesPage


class TextSearchPage(MyImagesPage):
    # 打开“我的图片”页面后切到文搜图页签，聚焦文本检索场景。
    def open_page(self) -> None:
        super().open_page()
        self.switch_tab("文搜图")

    # 读取文搜图输入框占位文案，校验引导提示是否正确。
    def text_search_input_placeholder(self) -> str:
        return self.find(By.CSS_SELECTOR, ".text-search-input input").get_attribute("placeholder")

    # 判断文搜图按钮是否可用，用于验证查询词必填规则。
    def text_search_button_enabled(self) -> bool:
        return self.is_enabled(By.CSS_SELECTOR, ".text-search-btn")

    # 在文搜图输入框中输入查询语句，驱动文本检索流程。
    def input_text_query(self, query: str) -> None:
        self.type(By.CSS_SELECTOR, ".text-search-input input", query)

    # 提交文搜图请求，触发图片检索。
    def submit_text_search(self) -> None:
        self.click(By.CSS_SELECTOR, ".text-search-btn")
