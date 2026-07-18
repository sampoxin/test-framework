"""
小程序 UI 测试公共 fixture（pytest 模式）

运行方式：
    pytest testcases/miniapp/ -v --no-cov

说明：
    - MiniTest 继承自 unittest.TestCase，pytest 原生支持运行
    - setUpClass 自动触发 _miniClassSetUp，初始化 minium 连接
    - 需在 setUpClass 前预设 CONFIG（minium 默认从 CWD 查找 config.json）
    - ensure_logged_in 作为 autouse fixture，每个测试方法执行前自动检查登录状态
"""
import os
import pytest
import minium
from minium.framework.miniconfig import MiniConfig
from minium.framework.minitest import MiniTest
from mini.common.actions import ensure_logged_in
from mini.pages.userinfo_page import UserInfoPage
from mini.pages.login_page import LoginPage
from mini.pages.personal_page import PersonalPage
from utils.logger import logger

# ============================================================
# 模块加载时设置 MiniTest.CONFIG（早于 setUpClass 执行）
# pytest 在 collection 阶段导入 conftest.py，此时设置 CONFIG
# 确保后续 setUpClass → setUpConfig 不会因找不到 config.json 而报错
# ============================================================
_mini_config_path = os.path.join(os.getcwd(), "mini", "config.json")
MiniTest.CONFIG = MiniConfig.from_file(_mini_config_path)


# ============================================================
# 会话级登录状态标记：只在首个非 skip_login 用例时检查一次
# ============================================================
_session_logged_in = False


@pytest.fixture(autouse=True)
def _ensure_logged_in(request):
    """
    会话级自动登录检查：
    - 仅在首个非 skip_login 用例执行时检查登录状态
    - 后续用例直接跳过，避免每个用例都跳转个人中心页
    - 在测试类或方法上添加 @pytest.mark.skip_login 可跳过自动登录
    """
    global _session_logged_in

    # 检查 skip_login 标记（类级别或方法级别）
    marker = request.node.get_closest_marker("skip_login")
    if marker:
        logger.info("检测到 skip_login 标记，跳过自动登录")
        return

    # 已在本会话中完成过登录检查，直接跳过
    if _session_logged_in:
        return

    instance = request.instance
    if isinstance(instance, MiniTest):
        _session_logged_in = ensure_logged_in(instance)


@pytest.fixture
def userinfo_page(request):
    """注入 UserInfoPage"""
    return UserInfoPage(request.instance)


@pytest.fixture
def login_page(request):
    """注入 LoginPage"""
    return LoginPage(request.instance)


@pytest.fixture
def personal_page(request):
    """注入 PersonalPage"""
    return PersonalPage(request.instance)
