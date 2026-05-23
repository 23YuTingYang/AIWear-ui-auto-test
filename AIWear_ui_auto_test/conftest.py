from __future__ import annotations

from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.edit_page import EditPage
from pages.login_page import LoginPage
from pages.my_images_page import MyImagesPage
from utils.driver_utils import create_driver
from utils.redis_utils import RedisClient
from utils.screenshot_utils import save_failure_screenshot
from utils.yaml_utils import load_yaml

PROJECT_ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
# 返回 UI 自动化项目根目录。
# 这是一切配置文件、截图目录和日志目录的统一定位基准，避免在各处手写相对路径。
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
# 加载环境配置。
# 这里集中提供 base_url、浏览器模式、等待时间、Redis 和测试资源路径等全局参数。
def env_settings(project_root):
    return load_yaml(project_root / "config" / "env.yaml")


@pytest.fixture(scope="session")
# 加载测试账号配置。
# 账号与邮箱信息统一放在配置文件中，测试代码只消费，不直接硬编码凭据。
def account_settings(project_root):
    return load_yaml(project_root / "config" / "account.yaml")


@pytest.fixture(scope="session")
# 提取图片路径配置。
# 图片上传、编辑、合并、图搜图都依赖这些路径，单独提取后可减少重复解析。
def image_paths(env_settings, project_root):
    paths = {}
    for key, value in env_settings["paths"].items():
        path = Path(value)
        if not path.is_absolute():
            path = project_root / path
        paths[key] = str(path)
    return paths


@pytest.fixture(scope="session")
# 初始化 Redis 客户端并在会话结束时释放连接。
# 如果 Redis 当前不可用，则返回 None，让验证码类场景自行决定跳过，而不是让整套测试直接中断。
def redis_client(env_settings):
    redis_settings = env_settings["redis"]
    client = RedisClient(
        host=redis_settings["host"],
        port=int(redis_settings["port"]),
        db=int(redis_settings.get("db", 0)),
        password=redis_settings.get("password"),
        socket_timeout=int(redis_settings.get("socket_timeout", 5)),
        verification_prefix=redis_settings.get("verification_prefix", "verification:code:"),
    )
    try:
        client.ping()
    except Exception:
        client = None
    yield client
    if client is not None:
        client.close()


# 复用单次登录会话。
# 设计目标是让依赖登录态的测试模块共享一个已登录浏览器，减少每个模块重复登录带来的时间开销。
# 实现策略是先访问业务页判断是否已有登录态；若没有，则回到登录页执行一次密码登录。
def _login_once(driver, env_settings, account_settings, project_root):
    # 创建编辑页页面对象，用于打开业务页并检查是否已登录
    edit_page = EditPage(driver, env_settings, project_root)
    # 打开编辑页
    edit_page.open_page()
    try:
        edit_page.visible(By.CSS_SELECTOR, ".app-header-trigger", timeout=5)
        edit_page.visible(By.CSS_SELECTOR, ".menu-item", timeout=5)
        return driver
    except TimeoutException:
        pass

    # 创建登录页页面对象。
    page = LoginPage(driver, env_settings, project_root)
    page.open_page()
    page.visible(By.CSS_SELECTOR, "button.submit", timeout=5)
    # 切换到密码登录
    page.switch_to_password_login()
    page.input_username(account_settings["password_login"]["username"])
    page.input_password(account_settings["password_login"]["password"])
    page.submit()
    edit_page.visible(By.CSS_SELECTOR, ".app-header-trigger", timeout=10)
    edit_page.visible(By.CSS_SELECTOR, ".menu-item", timeout=10)
    return driver


@pytest.fixture(scope="session")
# 创建浏览器驱动，并在整个测试会话结束后统一关闭。
# 作用域使用 session，表示整套 UI 自动化默认共享一个浏览器实例。
def driver(env_settings):
    driver = create_driver(env_settings)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
# 提供已登录的浏览器驱动。
# 依赖它的测试模块默认可以直接进入业务页，无需各自处理登录前置动作。
def logged_in_driver(driver, env_settings, account_settings, project_root):
    return _login_once(driver, env_settings, account_settings, project_root)


@pytest.fixture(scope="session")
# 确保关键测试图片已存在于“我的图片”中。
# 这是编辑和合并场景的共享前置条件，避免单个测试因为缺少素材而失败。
def prepared_images(logged_in_driver, env_settings, project_root, image_paths):
    # 创建“我的图片”页面对象。
    # 这里使用 logged_in_driver，说明进入该页面前必须已有登录态。
    page = MyImagesPage(logged_in_driver, env_settings, project_root)
    page.open_page()
    page.wait_path("/images", timeout=10)

    required_images = [
        image_paths["person_female"],
        image_paths["cloth_red"],
    ]
    # 读取当前“我的图片”页面已有图片名称，并转成集合。 转成 set 的好处是后面判断某个名称是否存在更快、更直接。
    existing_names = set(page.image_names())
    for image_path in required_images:
        # 从图片路径中提取不带扩展名的文件名
        image_name = Path(image_path).stem
        if image_name in existing_names:
            continue
        page.upload_image(image_path)
        page.wait_image_name(image_name, timeout=10)
        existing_names = set(page.image_names())
    return True


@pytest.hookimpl(hookwrapper=True)
# 在测试失败时自动截图并附加到 Allure 报告。
# 只处理测试执行阶段的失败，不处理 setup/teardown，避免把前置初始化波动和业务断言失败混在一起。
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    # item.funcargs 保存当前测试用例实际使用过的 fixture。
    driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
    project_root = item.funcargs.get("project_root")
    if not driver or not project_root:
        return

    screenshot_path = save_failure_screenshot(driver, project_root, item.name)
    with open(screenshot_path, "rb") as file:
        # 附加到 Allure 报告
        allure.attach(file.read(), name=item.name, attachment_type=allure.attachment_type.PNG)
