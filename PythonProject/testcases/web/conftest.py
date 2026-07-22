"""
后台管理系统 UI 测试公共 fixture（Playwright）

pytest-playwright 自动提供以下内置 fixture:
    - page: 每个测试方法独立的 Page 实例
    - browser: 会话级 Browser 实例
    - context: 会话级 BrowserContext 实例

全局速度控制：
    --slowmo N    每个 Playwright 操作后等待 N 毫秒（默认 100）
                  调试时可加大，如: pytest --slowmo 500
                  CI 可关闭，如: pytest --slowmo 0
"""
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
    slow_mo = int(request.config.getoption("--slowmo", default=100))
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


# ==================== 页面 fixture ====================

@pytest.fixture(scope="session")
def admin_page(browser):
    """
    已登录的后台管理页面（session 级，只登录一次）
    手动创建 context + page，避免与 function 级 fixture 冲突
    """
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(account="15973199394", password="12345")
    # 显式等待 URL 离开登录页，最多 10 秒
    try:
        page.wait_for_url("**/dashboard**", timeout=10000)
    except Exception:
        pass  # URL 可能不是 dashboard，只要不是 login 就行
    assert login_page.is_login_success(), f"后台登录失败，当前URL: {page.url}"
    logger.info("后台管理系统登录成功")
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
    每个用例执行前确保页面处于稳定状态
    autouse=True：所有 web 用例自动生效，无需手动引用
    """
    try:
        admin_page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass  # 超时不阻塞，让用例自己处理
