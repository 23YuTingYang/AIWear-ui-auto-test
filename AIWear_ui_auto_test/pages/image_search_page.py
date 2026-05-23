from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.my_images_page import MyImagesPage


class ImageSearchPage(MyImagesPage):
    # 打开“我的图片”页面后切到图搜图页签，聚焦以图搜图场景。
    def open_page(self) -> None:
        super().open_page()
        self.switch_tab("图搜图")

    # 判断图搜图按钮是否可用，用于验证搜索图片是否已上传。
    def image_search_button_enabled(self) -> bool:
        return self.is_enabled(By.CSS_SELECTOR, ".image-search-btn")

    # 上传图搜图参考图片，供以图搜图场景使用。
    def upload_search_image(self, file_path: str) -> None:
        self.send_file_to_input(file_path, (By.CSS_SELECTOR, ".image-search-select-wrap"))

    # 提交图搜图请求，触发相似图片检索。
    def submit_image_search(self) -> None:
        self.click(By.CSS_SELECTOR, ".image-search-btn")

    # 获取图搜图上传区域的占位文本，校验空状态提示。
    def image_search_placeholder(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".image-search-select-text")
