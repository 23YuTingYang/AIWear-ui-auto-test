from __future__ import annotations

from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.wait_utils import build_wait


class MergePage(BasePage):
    PATH = "/merge"

    # 打开图片合并页面，作为合并场景测试入口。
    def open_page(self) -> None:
        self.open(self.PATH)

    # 选择第一张图片，默认取预置的人像素材作为主体图。
    def upload_image1(self, image_name: str | None = None) -> None:
        selected_name = image_name or Path(self.settings["paths"]["person_female"]).stem
        self.click(By.CSS_SELECTOR, ".merge-select-btn")
        self.select_image_from_modal_by_label(selected_name)

    # 选择第二张图片，默认取预置的服装素材作为替换来源。
    def upload_image2(self, image_name: str | None = None) -> None:
        selected_name = image_name or Path(self.settings["paths"]["cloth_red"]).stem
        self.click(By.CSS_SELECTOR, ".merge-select-btn")
        self.select_image_from_modal_by_label(selected_name)

    # 输入合并指令，描述图片合并的业务意图。
    def input_instruction(self, text: str) -> None:
        self.type(By.CSS_SELECTOR, ".merge-textarea", text)

    # 点击合并提交按钮，发起图片合并任务。
    def submit(self) -> None:
        self.click(By.CSS_SELECTOR, ".merge-submit-btn")

    # 判断合并按钮是否可点击，用于校验输入条件是否满足。
    def submit_enabled(self) -> bool:
        return self.is_enabled(By.CSS_SELECTOR, ".merge-submit-btn")

    # 等待提交后进入 AI 计算中状态，证明合并请求已被触发。
    def wait_merge_loading(self, timeout: int = 10) -> None:
        self.visible(By.CSS_SELECTOR, ".loading-message", timeout)

    # 等待合并结果图出现，单独放宽到 30 秒以适配 AI 合并耗时。
    def wait_merge_result(self, timeout: int = 90) -> None:
        build_wait(self.driver, timeout, self.poll_frequency).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".merge-result-img"))
        )

    # 获取合并页主标题，校验页面展示是否正确。
    def hero_title(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".page-title")

    # 获取合并输入框占位文案，验证用户提示信息。
    def textarea_placeholder(self) -> str:
        return self.find(By.CSS_SELECTOR, ".merge-textarea").get_attribute("placeholder")
