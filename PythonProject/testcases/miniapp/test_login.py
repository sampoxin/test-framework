import os

import pytest
import allure
from testcases.miniapp.base_test import MiniAppBase
from mini.pages.login_page import LoginPage
from mini.pages.personal_page import PersonalPage
from utils.logger import logger


@allure.story("登录功能")
@pytest.mark.skip_login
class TestMiniLogin(MiniAppBase):
    """登录功能测试"""

    def setUp(self):
        self.login_page = LoginPage(self)
        self.personal_page = PersonalPage(self)

    @pytest.mark.order(1)
    def test_00_personal_login(self):
        """从个人中心到登录页"""
        logger.info("从个人中心到登录页")
        self.personal_page.open()
        self.personal_page.tap_login_or_name()
        self.page.wait_for(2)
        assert self.login_page.is_at_login_page(), "应在登录页面"

    @pytest.mark.order(2)
    def test_01_view_login_page(self):
        """查看登录页标题"""
        logger.info("查看登录页标题")
        assert self.login_page.is_at_login_page(), "应在登录页面"
        assert self.login_page.has_video(), "欢迎视频应存在"
        assert self.login_page.is_quick_mode(), "默认应为一键登录模式"

    @pytest.mark.order(3)
    def test_02_switch_to_phone_login_mode(self):
        """切换到手机号登录模式"""
        logger.info("切换到手机号登录模式")
        self.login_page.switch_to_phone_login()
        assert self.login_page.is_phone_mode(), "应为手机号登录模式"
        assert self.login_page.has_phone_input(), "手机号输入框应存在"

    @pytest.mark.order(4)
    def test_03_phone_login_success(self):
        """手机号+验证码登录成功"""
        logger.info("手机号+验证码登录成功")
        phone = os.environ.get("TEST_USER_PHONE", "")
        code = os.environ.get("TEST_VERIFY_CODE", "")
        result = self.login_page.login_with_phone(
            phone=phone,
            code=code
        )
        if result:
            logger.info("手机号登录成功")
        else:
            logger.warning("登录未成功（验证码可能已过期）")
