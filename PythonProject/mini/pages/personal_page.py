"""个人中心页 Page Object"""
from typing import Any, Optional

import allure
import minium
from .base_page import BasePage
from utils.logger import logger


class PersonalPage(BasePage):
    """我的页"""
    PATH = "/pages/personal/index"

    CSS_NAME_BOX = ".name-box_GTmAM"
    CSS_LOGIN_BOX = ".login-box_p0h9P"

    def __init__(self, mini: Any) -> None:
        """
        Args:
            mini: minium.MiniTest 实例，提供 self.page / self.app
        """
        super().__init__(mini)

    @allure.step("打开个人中心")
    def open(self) -> "PersonalPage":
        """跳转到我的页面"""
        self.switch_tab(self.PATH)
        return self

    # ========== 页面判断 ==========

    def is_at_personal_page(self) -> bool:
        """是否在个人中心页"""
        return "personal" in self.get_page_path()

    def login_or_user_box(self, max_timeout: int = 5) -> Optional[Any]:
        """用户框（已登录返回 name-box，未登录返回 login-box）"""
        name_box = self.find_element(self.CSS_NAME_BOX, max_timeout=max_timeout)
        if name_box:
            return name_box
        return self.find_element(self.CSS_LOGIN_BOX, max_timeout=max_timeout)

    def is_logged_in(self) -> bool:
        """是否登录"""
        return self.find_element(self.CSS_NAME_BOX, max_timeout=5) is not None

    @allure.step("点击登录/用户名框")
    def tap_login_or_name(self) -> "PersonalPage":
        """点击登录框或用户名框"""
        element = self.login_or_user_box()
        if element:
            element.tap()
        else:
            logger.warning("未找到登录框或用户名框")
        return self

    def wait_for_login_or_name(self) -> bool:
        """等待登录框或用户名框加载"""
        return self.wait_for_page(self.PATH)
