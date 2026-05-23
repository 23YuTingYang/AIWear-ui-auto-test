from __future__ import annotations

from pathlib import Path

import pytest

from pages.image_search_page import ImageSearchPage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "image_search.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(4)
class TestImageSearch:
    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖图搜图页签的按钮状态、搜索结果、空状态和页签切换等行为。
    def test_image_search(self, logged_in_driver, env_settings, project_root, image_paths, prepared_images, case):
        page = ImageSearchPage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case_id == "image_search_enable_button":
            page.upload_search_image(image_paths[case["image_key"]])
            assert page.image_search_button_enabled()
            return

        if case_id == "image_search_disable_without_image":
            assert not page.image_search_button_enabled()
            return

        if case_id == "image_search_show_results":
            page.upload_search_image(image_paths[case["image_key"]])
            page.submit_image_search()
            page.wait_image_count_at_least(1)
            assert page.active_tab_text() == "图搜图"
            assert len(page.image_cards()) >= 1
            assert len(page.image_names()) >= 1
            return

        if case_id == "image_search_placeholder":
            assert page.image_search_placeholder() == "请选择图片"
            return

        if case_id == "image_search_tab_highlight":
            assert page.active_tab_text() == "图搜图"
            return

        if case_id == "image_search_empty_state":
            page.upload_search_image(image_paths[case["image_key"]])
            page.submit_image_search()
            page.wait_empty_state_text("找找看，这里有你的素材~")
            assert page.active_tab_text() == "图搜图"
            assert page.empty_state_text() == "找找看，这里有你的素材~"
            return

        if case_id == "image_search_menu_highlight":
            assert page.active_menu_text() == "我的图片"
            assert page.title() == "我的图片"
            return

        if case_id == "image_search_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return

        if case_id == "image_search_switch_back":
            page.switch_tab("文搜图")
            page.switch_tab("图搜图")
            assert page.active_tab_text() == "图搜图"
            assert page.is_displayed(*("css selector", ".image-search-select-wrap"))
            assert page.is_displayed(*("css selector", ".image-search-btn"))
            return



