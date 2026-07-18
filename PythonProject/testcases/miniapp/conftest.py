"""
小程序 UI 测试公共 fixture（pytest 模式使用）
若使用 python -m minium 运行，此文件不生效
"""
import pytest
from mini.pages.login_page import LoginPage


@pytest.fixture(scope="function")
def pages(mini_test):
    """
    注入页面对象，测试方法直接用 pages.login
    注意：pytest 模式下需额外提供 mini_test fixture
    """
    class Pages:
        login = LoginPage(mini_test)
    return Pages()
