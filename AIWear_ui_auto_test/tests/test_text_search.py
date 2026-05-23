from __future__ import annotations

from pathlib import Path

import pytest

from pages.text_search_page import TextSearchPage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "text_search.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(3)
class TestTextSearch:
    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖文搜图页签的按钮状态、搜索结果、空状态和页签切换等行为。
    def test_text_search(self, logged_in_driver, env_settings, project_root, prepared_images, case):
        page = TextSearchPage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case_id == "text_search_enable_button":
            page.input_text_query(case["query"])
            assert page.text_search_button_enabled()
            return

        if case_id == "text_search_disable_without_query":
            assert not page.text_search_button_enabled()
            return

        if case_id == "text_search_show_results":
            page.input_text_query(case["query"])
            page.submit_text_search()
            page.wait_image_count_at_least(1)
            assert page.active_tab_text() == "文搜图"
            assert len(page.image_cards()) >= 1
            assert len(page.image_names()) >= 1
            return

        if case_id == "text_search_placeholder":
            assert page.text_search_input_placeholder() == "请输入查询内容"
            return

        if case_id == "text_search_tab_highlight":
            assert page.active_tab_text() == "文搜图"
            return

        if case_id == "text_search_empty_state":
            page.input_text_query(case["query"])
            page.submit_text_search()
            page.wait_empty_state_text("找找看，这里有你的素材~")
            assert page.active_tab_text() == "文搜图"
            assert page.empty_state_text() == "找找看，这里有你的素材~"
            return

        if case_id == "text_search_menu_highlight":
            assert page.active_menu_text() == "我的图片"
            assert page.title() == "我的图片"
            return

        if case_id == "text_search_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return

        if case_id == "text_search_switch_back":
            page.switch_tab("图搜图")
            page.switch_tab("文搜图")
            assert page.active_tab_text() == "文搜图"
            assert page.is_displayed(*("css selector", ".text-search-input input"))
            assert page.is_displayed(*("css selector", ".text-search-btn"))
            return
