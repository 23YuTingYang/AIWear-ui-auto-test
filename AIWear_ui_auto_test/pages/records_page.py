from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class RecordsPage(BasePage):
    PATH = "/records"

    # 打开历史记录页，并等待表格或空状态渲染完成。
    def open_page(self) -> None:
        self.open(self.PATH)
        self._wait(10).until(
            #只要里面有一个结果是 True，整体就是 True
            lambda driver: any(
                element.is_displayed()
                for element in driver.find_elements(By.CSS_SELECTOR, ".records-table, .empty-state")
            )
        )

    # 获取历史记录页头部标题，校验页面跳转是否正确。
    def header_title(self) -> str:
        return self.text_of(By.CSS_SELECTOR, ".app-header-title")

    # 读取表格表头列表，用于核对记录页字段顺序和名称。
    def table_headers(self) -> list[str]:
        return self.get_visible_texts(By.CSS_SELECTOR, ".el-table__header .cell")

    # 统计当前可见记录行数，判断是否存在历史数据。
    def row_count(self) -> int:
        return len([row for row in self.driver.find_elements(By.CSS_SELECTOR, ".records-table .el-table__row") if row.is_displayed()])

    # 提取记录中的操作类型文案，供筛选结果断言复用。
    def action_types(self) -> list[str]:
        return self.get_visible_texts(By.CSS_SELECTOR, ".records-table .action-badge")

    # 展开筛选下拉菜单，进入记录类型筛选流程。
    def open_filter(self) -> None:
        self.click(By.CSS_SELECTOR, ".filter-trigger")

    # 获取筛选菜单中的可选项，校验筛选能力是否完整展示。
    def filter_options(self) -> list[str]:
        self.open_filter()
        self._wait(10).until(
            lambda driver: any(
                element.is_displayed()
                for element in driver.find_elements(By.CSS_SELECTOR, ".el-dropdown-menu__item")
            )
        )
        return [text for text in self.get_visible_texts(By.CSS_SELECTOR, ".el-dropdown-menu__item") if text]

    # 按给定文案选择筛选项，驱动历史记录过滤逻辑。
    def choose_filter(self, option_text: str) -> None:
        self.open_filter()
        self.click(By.XPATH, f"//li[contains(@class,'el-dropdown-menu__item') and normalize-space(.)='{option_text}']")

    # 判断编辑记录是否存在第二张图片占位为“-”的行，验证表格展示规则。
    def has_edit_row_with_dash(self) -> bool:
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".records-table .el-table__row")
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td .cell")
            texts = [cell.text.strip() for cell in cells]
            if len(texts) >= 4 and "图片编辑" in texts[1] and texts[3] == "-":
                return True
        return False

    # 判断首行结果列是否包含结果图，验证记录结果展示是否完整。
    def first_row_has_result_image(self) -> bool:
        rows = [row for row in self.driver.find_elements(By.CSS_SELECTOR, ".records-table .el-table__row") if row.is_displayed()]
        if not rows:
            return False
        cells = rows[0].find_elements(By.CSS_SELECTOR, "td")
        if not cells:
            return False
        return bool(cells[-1].find_elements(By.CSS_SELECTOR, ".cell-thumb img"))
