from __future__ import annotations

from pathlib import Path

import pytest

from pages.records_page import RecordsPage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "records.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(7)
class TestRecords:
    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖历史记录页的表格展示、筛选逻辑、结果图展示和用户菜单行为。
    def test_records(self, logged_in_driver, env_settings, project_root, case):
        page = RecordsPage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case_id == "records_default_table":
            assert page.header_title() == "历史记录"
            assert page.is_displayed(*("css selector", ".records-table"))
            assert page.row_count() >= 1
            return

        if case_id == "records_headers":
            headers = page.table_headers()
            assert headers[:6] == ["序号", "类型", "图片1", "图片2", "指令", "执行结果"]
            return

        if case_id == "records_row_content":
            assert page.row_count() >= 1
            assert len(page.action_types()) >= 1
            assert page.first_row_has_result_image()
            return

        if case_id == "records_filter_expand":
            assert page.filter_options() == ["全部记录", "图片编辑", "图片合并"]
            return

        if case_id == "records_filter_edit":
            page.choose_filter("图片编辑")
            assert page.row_count() >= 1
            #断言每一条记录都是图片编辑
            assert all(text == "图片编辑" for text in page.action_types())
            return

        if case_id == "records_filter_merge":
            page.choose_filter("图片合并")
            assert page.row_count() >= 1
            # 断言每一条记录都是图片合并
            assert all(text == "图片合并" for text in page.action_types())
            return

        if case_id == "records_edit_second_column_placeholder":
            assert page.has_edit_row_with_dash()
            return

        if case_id == "records_menu_highlight":
            assert page.active_menu_text() == "历史记录"
            return

        if case_id == "records_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return
