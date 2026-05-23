from __future__ import annotations

from pathlib import Path

import pytest

from pages.edit_page import EditPage
from pages.login_page import LoginPage
from utils.yaml_utils import load_yaml

#读取 YAML 里的测试数据
DATA = load_yaml(Path(__file__).resolve().parents[1] / "data" / "login.yaml")["cases"]
#定义用例顺序表
CASE_ORDER = {
    "login_default_code_form": 1,
    "login_switch_to_password_form": 2,
    "login_invalid_email_format": 3,
    "login_invalid_code": 4,
    "login_code_success": 5,
    "login_refresh_keeps_session": 6,
    "login_invalid_password": 7,
    "logout_redirects_to_login": 8,
    "login_password_success": 9,
}
#按顺序排序用例 查不到排到最后面
DATA = sorted(DATA, key=lambda case: CASE_ORDER.get(case["id"], 999))

# 把 YAML 中声明的 marker 名称转换为 pytest marker 对象，供参数化用例挂载标签。
def _marks(case):
    return [getattr(pytest.mark, marker) for marker in case.get("markers", [])]

# 统一校验“当前页面已经处于登录态”
# 统一校验登录后的头部状态，确认用户信息和登录入口已正确展示。
def _assert_logged_in_header(page, account_settings):
    assert page.is_displayed(*("css selector", ".app-header-trigger"))
    assert (
        page.has_text(account_settings["email_login"]["email"], timeout=2)
        or page.has_text(account_settings["password_login"]["username"], timeout=2)
    )

# 封装密码登录表单填写动作，减少多个登录场景中的重复输入代码。
def _fill_password_login_form(page, username, password):
    page.switch_to_password_login()
    page.input_username(username)
    page.input_password(password)

# 在需要验证未登录态前主动退出，避免旧会话影响登录用例结果。
def _logout_if_logged_in(driver, env_settings, project_root):
    edit_page = EditPage(driver, env_settings, project_root)
    edit_page.open_page()
    if edit_page.is_displayed(*("css selector", ".app-header-trigger"), timeout=3):
        edit_page.logout()
        return True
    return False


@pytest.mark.order(1)
class TestLogin:
    # 登录模块放在最前执行。
    # 原因是它既验证登录本身，又为后续依赖登录态的场景提供稳定的会话基础。

    @pytest.mark.parametrize("case", [pytest.param(case, id=case["id"], marks=_marks(case)) for case in DATA])
    # 覆盖登录页默认展示、验证码登录、密码登录、会话保持和退出登录等核心登录流程。
    def test_login(self, driver, env_settings, account_settings, project_root, redis_client, case):
        case_id = case["id"]

        # 这个场景依赖“已登录态”，因此不走统一的登出前置逻辑。
        if case_id == "login_refresh_keeps_session":
            edit_page = EditPage(driver, env_settings, project_root)
            #1.打开编辑页。
            edit_page.open_page()
            #2.等待用户名可见
            edit_page.visible(*("css selector", ".app-header-trigger"), timeout=10)
            #3.等待左边菜单栏可见
            edit_page.visible(*("css selector", ".menu-item"), timeout=10)
            #4.刷新页面  用于验证刷新后登录状态是否仍然保持。
            driver.refresh()
            #5.等待当前路径是不是 /edit
            edit_page.wait_path(case["expect_url"])
            #6.断言当前路径以是不是 /edit 结尾
            assert edit_page.current_path().endswith(case["expect_url"])
            # 7.断言当前页面标题
            assert edit_page.text_of(*("css selector", ".app-header-title")) == case["expect_title"]
            _assert_logged_in_header(edit_page, account_settings)
            return

        # 先登出，避免旧会话干扰后续登录态验证。
        _logout_if_logged_in(driver, env_settings, project_root)

        page = LoginPage(driver, env_settings, project_root)
        page.open_page()

        if case_id == "login_default_code_form":
            assert page.is_code_login_active()
            assert page.is_displayed(*("css selector", "input[placeholder='请输入邮箱']"))
            assert page.is_displayed(*("css selector", "input[placeholder='请输入验证码']"))
            assert page.is_displayed(*("css selector", ".send-link-suffix"))
            assert not page.password_field_visible(timeout=2)
            return

        if case_id == "login_switch_to_password_form":
            page.switch_to_password_login()
            assert page.is_password_login_active()
            assert page.is_displayed(*("css selector", "input[placeholder='请输入用户名']"))
            assert page.is_displayed(*("css selector", "input[placeholder='请输入密码']"))
            assert not page.code_field_visible(timeout=2)
            assert page.text_of(*("css selector", "button.submit")) == "登录/注册"
            return

        if case_id == "logout_redirects_to_login":
            _fill_password_login_form(page, case["username"], case["password"])
            page.submit()
            edit_page = EditPage(driver, env_settings, project_root)
            edit_page.wait_path("/edit")
            edit_page.logout()
            page.wait_path("/login")
            page.open(case["protected_path"])  #主动访问受保护页面 /edit
            page.wait_path("/login")
            assert page.current_path().endswith("/login")
            assert not page.is_displayed(*("css selector", ".app-header-trigger"), timeout=2)
            return
        #密码登录的操作
        if case["login_type"] == "password":
            _fill_password_login_form(page, case["username"], case["password"])
        else:
            page.switch_to_code_login()
            page.input_email(case["email"])

        if case_id == "login_invalid_email_format":
            page.click_send_code()
            assert page.current_path().endswith("/login")
            assert not page.has_text(case["expect_not_text"], timeout=2)
            return

        if case_id == "login_code_success":
            # 验证码登录强依赖 Redis 和后端异步写入；环境不满足时直接跳过，避免误报脚本问题。
            if redis_client is None:
                pytest.skip("Redis 不可用，跳过验证码登录场景")
            page.click_send_code()
            code = redis_client.wait_for_verification_code(case["email"], timeout=5.0, poll_interval=0.5)
            if not code:
                pytest.skip("未读取到验证码，跳过验证码登录场景")
            page.input_code(code)
        elif case_id == "login_invalid_code":
            page.input_code(case["code"])

        #把前面不同分支准备好的数据真正送出去，让页面执行登录请求。
        page.submit()

        #登录成功后的统一断言
        if case_id in {"login_password_success", "login_code_success"}:
            edit_page = EditPage(driver, env_settings, project_root)
            edit_page.wait_path(case["expect_url"])
            assert edit_page.current_path().endswith(case["expect_url"])
            assert edit_page.text_of(*("css selector", ".app-header-title")) == case["expect_title"]
            _assert_logged_in_header(edit_page, account_settings)
            return

        #登录失败后的统一断言
        if case_id in {"login_invalid_code", "login_invalid_password"}:
            assert page.current_path().endswith("/login")
            assert page.has_text(case["expect_error"])
            assert not page.is_displayed(*("css selector", ".app-header-trigger"), timeout=2)
            return
