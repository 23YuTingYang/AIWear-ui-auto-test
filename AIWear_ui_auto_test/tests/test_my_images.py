from __future__ import annotations

from pathlib import Path

import pytest

from pages.my_images_page import MyImagesPage
from utils.yaml_utils import load_yaml


DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "my_images.yaml")["cases"]

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]


@pytest.mark.order(2)
class TestMyImages:
    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖“我的图片”页面的上传、默认布局、页签切换和头部交互行为。
    def test_my_images(self, logged_in_driver, env_settings, project_root, image_paths, case):
        page = MyImagesPage(logged_in_driver, env_settings, project_root)
        page.open_page()
        case_id = case["id"]

        if case_id == "my_images_upload_success":
            before_count = len(page.image_cards())
            image_path = image_paths[case["image_key"]]
            page.upload_image(image_path)
            # 图片路径里取“文件名主体”，不包含后缀。等待页面中出现这个图片名称
            page.wait_image_name(Path(image_path).stem)
            after_count = len(page.image_cards())
            assert after_count >= before_count
            assert page.title() == "我的图片"
            return

        if case_id == "my_images_default_tab":
            assert page.title() == "我的图片"
            assert page.active_tab_text() == "我的图片"
            assert len(page.image_cards()) >= 1
            return

        if case_id == "my_images_card_content":
            cards = page.image_cards()
            assert len(cards) >= 1
            assert len(page.image_names()) >= 1 #前面上传过图片了
            return

        if case_id == "my_images_switch_text_tab":
            page.switch_tab("文搜图")
            assert page.active_tab_text() == "文搜图"
            assert page.is_displayed(*("css selector", ".text-search-input input"))
            assert page.is_displayed(*("css selector", ".text-search-btn"))
            return

        if case_id == "my_images_switch_image_tab":
            page.switch_tab("图搜图")
            assert page.active_tab_text() == "图搜图"
            assert page.is_displayed(*("css selector", ".image-search-select-wrap"))
            assert page.is_displayed(*("css selector", ".image-search-btn"))
            return

        if case_id == "my_images_menu_highlight":
            assert page.active_menu_text() == "我的图片"
            return

        if case_id == "my_images_user_dropdown":
            page.open_user_dropdown()
            assert page.has_text("退出登录")
            return

        if case_id == "my_images_title_stays":
            page.switch_tab("文搜图")
            assert page.title() == "我的图片"
            page.switch_tab("图搜图")
            assert page.title() == "我的图片"
            return

        if case_id == "my_images_layout_ok":
            assert len(page.image_cards()) >= 1
            assert len(page.image_names()) >= 1
            return
