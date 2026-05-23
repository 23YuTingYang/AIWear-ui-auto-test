from __future__ import annotations

from pathlib import Path

import pytest

from pages.edit_page import EditPage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "edit.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(5)
class TestEdit:
    # 编辑模块依赖已登录态和预置素材，因此执行顺序放在图片准备相关场景之后。

    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖图片编辑页的提交条件、默认展示、导航跳转和用户菜单等核心行为。
    def test_edit(self, logged_in_driver, env_settings, project_root, prepared_images, case):
        page = EditPage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case_id == "edit_submit_success":
            page.upload_image()
            page.input_instruction(case["instruction"])
            assert page.submit_enabled()
            page.submit()
            page.wait_edit_loading()
            assert page.text_of(*("css selector", ".loading-message")) == "AI计算中..."
            return

        if case_id == "edit_result_visible":
            page.upload_image()
            page.input_instruction(case["instruction"])
            assert page.submit_enabled()
            page.submit()
            page.wait_edit_result()
            assert page.is_displayed(*("css selector", ".edit-result-img"))
            return

        if case_id == "edit_only_image":
            page.upload_image()
            assert not page.submit_enabled()
            return

        if case_id == "edit_only_instruction":
            page.input_instruction(case["instruction"])
            assert not page.submit_enabled()
            return

        if case_id == "edit_default_hero":
            assert page.text_of(*("css selector", ".app-header-title")) == "图片编辑"
            assert page.hero_title() == "单张图片编辑"
            assert page.is_displayed(*("css selector", ".edit-default-img"))
            return

        if case_id == "edit_menu_highlight":
            assert page.active_menu_text() == "图片编辑"
            return

        if case_id == "edit_placeholder":
            assert "描述您想呈现的画面" in page.textarea_placeholder()
            return

        if case_id == "edit_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return

        if case_id == "edit_jump_merge":
            page.click_menu("图片合并")
            page.wait_url_contains("/merge")
            assert page.current_path().endswith("/merge")
            assert page.text_of(*("css selector", ".app-header-title")) == "图片合并"
            return

        if case_id == "edit_jump_images":
            page.click_menu("我的图片")
            page.wait_url_contains("/images")
            assert page.current_path().endswith("/images")
            assert page.text_of(*("css selector", ".app-header-title")) == "我的图片"
            return
