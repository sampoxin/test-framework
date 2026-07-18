"""
登录页 Page Object
封装登录页的元素定位和操作，供测试用例调用
"""
import minium
from .base_page import BasePage
from utils.logger import logger
import time

class PersonalPage(BasePage):
    """我的页"""
    PATH = "/pages/personal/index"

    CSS_NAME_BOX = ".name-box_GTmAM"
    CSS_LOGIN_BOX = ".login-box_p0h9P"


    def __init__(self, mini: minium.Minium):
        """
        Args:
            mini: minium.Mini 实例，提供 self.page / self.app
        """
        super().__init__(mini)

    def open(self):
        """跳转到我的页面"""
        self.switch_tab(self.PATH)

    # ========== 页面判断 ==========
    def is_at_personal_page(self) -> bool:
        """是否在登录页"""
        return "personal" in self.get_page_path()

    def login_or_user_box(self, max_timeout=5):
        """用户框（已登录返回 name-box，未登录返回 login-box）"""
        name_box = self.find_element(self.CSS_NAME_BOX, max_timeout=max_timeout)
        if name_box:
            return name_box
        return self.find_element(self.CSS_LOGIN_BOX, max_timeout=max_timeout)

    def is_logged_in(self) -> bool:
        """是否登录"""
        return self.find_element(self.CSS_NAME_BOX, max_timeout=5) is not None

    def tap_login_or_name(self):
        """点击登录框或用户名框"""
        element = self.login_or_user_box()
        if element:
            element.tap()
        else:
            logger.warning("未找到登录框或用户名框")
        return self

    def wait_for_login_or_name(self):
        """等待登录框或用户名框加载"""
        return self.wait_for_page(self.PATH)
