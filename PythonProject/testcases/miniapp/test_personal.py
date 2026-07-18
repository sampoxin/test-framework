import minium
import pytest
import allure
from mini.pages.personal_page import PersonalPage
from mini.pages.login_page import LoginPage
from mini.pages.userinfo_page import UserInfoPage
from utils.logger import logger


@allure.story("个人中心")
class TestMiniPersonal(minium.MiniTest):
    """个人中心功能测试"""

    def setUp(self):
        self.personal_page = PersonalPage(self)
        self.login_page = LoginPage(self)
        self.user_info_page = UserInfoPage(self)

    @pytest.mark.order(10)
    def test_01_view_personal_page(self):
        """查看个人中心标题"""
        logger.info("查看个人中心标题")
        self.personal_page.open()
        self.personal_page.wait_for_login_or_name()
        assert self.personal_page.is_at_personal_page(), "应在个人中心页面"

    @pytest.mark.order(11)
    def test_02_tap_top_box(self):
        """点击顶部框（登录/未登录状态不同跳转）"""
        logger.info("点击顶部框")
        login_status = self.personal_page.is_logged_in()
        self.personal_page.tap_login_or_name()
        self.page.wait_for(2)
        if login_status:
            assert self.user_info_page.is_at_user_info_page(), "应在用户信息页页面"
            assert self.user_info_page.is_show_uid(), "应在用户信息页页面显示用户ID"
            self.user_info_page.to_back()
        else:
            assert self.login_page.is_at_login_page(), "应在登录页面"
            self.login_page.to_back()
        self.page.wait_for(2)
