from __future__ import annotations

from pathlib import Path

import pytest

from pages.merge_page import MergePage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "merge.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(6)
class TestMerge:
    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖图片合并页的素材选择、提交校验、默认展示和页面跳转行为。
    def test_merge(self, logged_in_driver, env_settings, project_root, prepared_images, image_paths, case):
        page = MergePage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case.get("image1_key"):
            page.upload_image1(Path(image_paths[case["image1_key"]]).stem)
        if case.get("image2_key"):
            page.upload_image2(Path(image_paths[case["image2_key"]]).stem)
        if case.get("instruction"):
            page.input_instruction(case["instruction"])

        if case_id == "merge_submit_success":
            assert page.submit_enabled()
            page.submit()
            page.wait_merge_loading()
            assert page.text_of(*("css selector", ".loading-message")) == "AI计算中..."
            return

        if case_id == "merge_result_visible":
            assert page.submit_enabled()
            page.submit()
            page.wait_merge_result()
            assert page.is_displayed(*("css selector", ".merge-result-img"))
            return

        if case_id in {"merge_missing_image1", "merge_missing_image2", "merge_missing_instruction"}:
            assert not page.submit_enabled()
            return

        if case_id == "merge_default_hero":
            assert page.text_of(*("css selector", ".app-header-title")) == "图片合并"
            assert page.hero_title() == "合并2张图片"
            assert page.is_displayed(*("css selector", ".merge-default-img"))
            return

        if case_id == "merge_menu_highlight":
            assert page.active_menu_text() == "图片合并"
            return

        if case_id == "merge_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return

        if case_id == "merge_placeholder":
            assert "给图2的人物换上图1的衣服" in page.textarea_placeholder()
            return

        if case_id == "merge_jump_records":
            page.click_menu("历史记录")
            page.wait_url_contains("/records")
            assert page.current_path().endswith("/records")
            assert page.text_of(*("css selector", ".app-header-title")) == "历史记录"
            return
