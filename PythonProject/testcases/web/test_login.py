"""后台管理系统 - 登录页测试"""
import pytest
import allure
from web.pages.login_page import LoginPage


@allure.story("后台登录")
class TestLogin:
    """登录功能测试"""

    @pytest.mark.order(1)
    def test_login_page_display(self, page):
        """登录页正常展示"""
        login_page = LoginPage(page)
        login_page.open()
        assert login_page.is_at_login_page(), "应显示登录页"

    @pytest.mark.order(2)
    @pytest.mark.parametrize("account, password", [("", "password")])
    def test_login(self, page, account, password):
        """空账号登录应提示错误"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(account, password)
        # 等待错误消息出现（替代 time.sleep）
        page.wait_for_timeout(1000)  # 等待服务端返回错误提示
        # 登录失败应仍在登录页
        assert login_page.is_at_login_page(), "登录失败"
