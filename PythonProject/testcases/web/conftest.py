"""
后台管理系统 UI 测试公共 fixture（Playwright）

pytest-playwright 自动提供以下内置 fixture:
    - page: 每个测试方法独立的 Page 实例
    - browser: 会话级 Browser 实例
    - context: 会话级 BrowserContext 实例

全局速度控制：
    --slowmo N    每个 Playwright 操作后等待 N 毫秒（默认 1000）
                  调试时可加大，如: pytest testcases/web/ --slowmo 500
                  CI 可关闭，如: pytest testcases/web/ --slowmo 0
                  注意：此选项仅影响 Playwright 操作，不影响 API/小程序测试
"""
import os

import allure
import pytest
from web.pages.login_page import LoginPage
from utils.logger import logger


# ==================== 浏览器配置 ====================

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, request):
    """
    浏览器启动参数
    --slowmo N 由 pytest-playwright 内置提供，控制每个操作后的等待毫秒数
    """
    slow_mo = int(request.config.getoption("--slowmo", default=1000))
    logger.info(f"Playwright slow_mo = {slow_mo}ms")
    return {
        **browser_type_launch_args,
        "headless": False,
        "slow_mo": slow_mo,
        "args": ["--start-fullscreen"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """浏览器上下文参数 - no_viewport 让页面自动适配窗口大小"""
    return {**browser_context_args, "no_viewport": True}


# ==================== 登录状态缓存 ====================
# 防止 session fixture 失败后被 pytest-rerunfailures 反复重建
_login_failed = False


# ==================== 页面 fixture ====================

@pytest.fixture(scope="session")
def admin_page(browser):
    """
    已登录的后台管理页面（session 级，只登录一次）
    手动创建 context + page，避免与 function 级 fixture 冲突

    登录策略：内置 3 次重试，全部失败后标记 _login_failed，
    后续用例自动 skip，不再重复触发登录。
    """
    global _login_failed

    if _login_failed:
        pytest.skip("后台登录已失败，跳过后续所有用例")

    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    login_page = LoginPage(page)

    # 从环境变量读取后台登录凭据（与 API 测试一致）
    admin_account = os.environ.get("ADMIN_ACCOUNT", "")
    admin_password = os.environ.get("ADMIN_PASSWORD_CIPHER", "")
    assert admin_account, "请检查 .env 中 ADMIN_ACCOUNT 是否配置"
    assert admin_password, "请检查 .env 中 ADMIN_PASSWORD 是否配置"

    # 内置 3 次登录重试，避免依赖 pytest-rerunfailures 对 session fixture 的无效重试
    last_error = None
    for attempt in range(1, 4):
        try:
            login_page.open()
            login_page.login(account=admin_account, password=admin_password)
            # 显式等待 URL 离开登录页，最多 10 秒
            try:
                page.wait_for_url("**/dashboard**", timeout=10000)
            except Exception:
                pass
            assert login_page.is_login_success(), f"后台登录失败，当前URL: {page.url}"
            logger.info(f"后台管理系统登录成功（第 {attempt} 次尝试）")
            break
        except Exception as e:
            last_error = e
            logger.warning(f"[登录重试] 第 {attempt}/3 次登录失败: {e}")
            if attempt < 3:
                page.reload()
                page.wait_for_timeout(2000)
    else:
        _login_failed = True
        context.close()
        pytest.fail(f"后台登录 3 次重试均失败: {last_error}")

    yield page
    context.close()


@pytest.fixture
def login_page(page):
    """注入 LoginPage"""
    return LoginPage(page)


# ==================== 用例间稳定性保障 ====================

@pytest.fixture(autouse=True)
def _stabilize_between_tests(admin_page):
    """
    每个用例执行前：
    1. 检查登录是否已失败 → 直接 skip
    2. 确保页面处于稳定状态
    """
    if _login_failed:
        pytest.skip("后台登录已失败，跳过后续所有用例")
    try:
        admin_page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass  # 超时不阻塞，让用例自己处理


# ==================== 失败自动截图 ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图并附加到 Allure 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 尝试从 fixture 获取 admin_page
        page = item.funcargs.get("admin_page") or item.funcargs.get("page")
        if page:
            try:
                screenshot_bytes = page.screenshot()
                allure.attach(
                    screenshot_bytes,
                    name=f"failure_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
                logger.info(f"[截图] 用例失败自动截图: {item.name}")
            except Exception as e:
                logger.warning(f"[截图] 自动截图失败: {e}")
