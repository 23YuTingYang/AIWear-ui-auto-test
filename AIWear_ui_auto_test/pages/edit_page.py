from __future__ import annotations

from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.wait_utils import build_wait


class EditPage(BasePage):
    PATH = "/edit"

    # 图片编辑页页面对象。
    # 当前只封装进入页面、选图、输入指令和提交等核心动作，不在这里处理测试断言。

    # 打开图片编辑页面，作为编辑场景测试的起点。
    def open_page(self) -> None:
        self.open(self.PATH)

    # 从图片选择弹窗中选择待编辑图片，默认使用预置的人像素材。
    def upload_image(self, image_name: str | None = None) -> None:
        selected_name = image_name or Path(self.settings["paths"]["person_female"]).stem
        self.click(By.CSS_SELECTOR, ".edit-select-btn")
        self.select_image_from_modal_by_label(selected_name)

    # 输入编辑指令，驱动“文字描述编辑图片”的核心业务流程。
    def input_instruction(self, text: str) -> None:
        self.type(By.CSS_SELECTOR, ".edit-textarea", text)

    # 点击编辑提交按钮，触发图片编辑任务执行。
    def submit(self) -> None:
        self.click(By.CSS_SELECTOR, ".edit-submit-btn")

    # 判断提交按钮是否可用，用于校验表单必填项约束。
    def submit_enabled(self) -> bool:
        return self.is_enabled(By.CSS_SELECTOR, ".edit-submit-btn")

    # 等待提交后进入 AI 计算中状态，证明编辑请求已被触发。
    def wait_edit_loading(self, timeout: int = 10) -> None:
        self.visible(By.CSS_SELECTOR, ".loading-message", timeout)

    # 等待编辑结果图出现，单独放宽到 30 秒以适配 AI 编辑耗时。
    def wait_edit_result(self, timeout: int = 30) -> None:
        build_wait(self.driver, timeout, self.poll_frequency).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".edit-result-img"))
        )

    # 读取页面主标题，校验编辑页文案是否正确。
    def hero_title(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".page-title")

    # 读取编辑输入框占位文案，验证页面引导信息。
    def textarea_placeholder(self) -> str:
        return self.find(By.CSS_SELECTOR, ".edit-textarea").get_attribute("placeholder")
