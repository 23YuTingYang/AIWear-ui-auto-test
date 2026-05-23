from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    # 登录页页面对象。
    # 这里封装的是登录页的业务动作，不负责决定具体断言分支；断言留在 tests 层完成。

    # 打开登录页，作为所有登录相关操作的统一入口。
    def open_page(self) -> None:
        self.open(self.PATH)

    # 切换到验证码登录页签，验证默认登录流程或验证码登录流程。
    def switch_to_code_login(self) -> None:
        self.click(By.XPATH, "//button[contains(@class,'tab') and normalize-space(.)='验证码登录']")

    # 切换到密码登录页签，供密码登录类用例复用。
    def switch_to_password_login(self) -> None:
        self.click(By.XPATH, "//button[contains(@class,'tab') and normalize-space(.)='密码登录']")

    # 在邮箱输入框中录入测试邮箱，驱动验证码登录前置输入。
    def input_email(self, email: str) -> None:
        self.type(By.CSS_SELECTOR, "input[placeholder='请输入邮箱']", email)

    # 在验证码输入框中填写验证码，完成验证码登录表单。
    def input_code(self, code: str) -> None:
        self.type(By.CSS_SELECTOR, "input[placeholder='请输入验证码']", code)

    # 在用户名输入框中填写账号名，供密码登录场景使用。
    def input_username(self, username: str) -> None:
        self.type(By.CSS_SELECTOR, "input[placeholder='请输入用户名']", username)

    # 在密码输入框中填写密码，完成密码登录表单。
    def input_password(self, password: str) -> None:
        self.type(By.CSS_SELECTOR, "input[placeholder='请输入密码']", password)

    # 点击发送验证码按钮，触发后端验证码下发逻辑。
    def click_send_code(self) -> None:
        self.click(By.CSS_SELECTOR, ".send-link-suffix")

    # 提交登录表单，统一触发登录动作。
    def submit(self) -> None:
        self.click(By.CSS_SELECTOR, "button.submit")

    # 判断当前是否处于验证码登录页签，用于校验默认展示状态。
    #如果里面包含 active，就认为当前验证码登录页签处于激活状态。
    def is_code_login_active(self) -> bool:
        return "active" in self.find(By.XPATH, "//button[contains(@class,'tab') and contains(normalize-space(.), '验证码登录')]").get_attribute("class")

    # 判断当前是否处于密码登录页签，用于校验切换结果。
    # 如果里面包含 active，就认为当前密码登录页签处于激活状态。
    def is_password_login_active(self) -> bool:
        return "active" in self.find(By.XPATH, "//button[contains(@class,'tab') and contains(normalize-space(.), '密码登录')]").get_attribute("class")

    # 判断密码输入框是否可见，支持带超时的状态断言。
    def password_field_visible(self, timeout: int | None = None) -> bool:
        return self.is_displayed(By.CSS_SELECTOR, "input[placeholder='请输入密码']", timeout)

    # 判断验证码输入框是否可见，用于区分页签切换后的表单状态。
    def code_field_visible(self, timeout: int | None = None) -> bool:
        return self.is_displayed(By.CSS_SELECTOR, "input[placeholder='请输入验证码']", timeout)
