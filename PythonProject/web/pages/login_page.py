"""后台管理系统 - 登录页 Page Object"""
import allure
from web.pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """登录页"""

    # 选择器
    INPUT_ACCOUNT = 'input[placeholder="请输入账号"]'
    INPUT_PASSWORD = 'input[placeholder="请输入密码"]'
    BTN_LOGIN = 'button:has-text("登 录")'

    @allure.step("打开登录页")
    def open(self) -> "LoginPage":
        """打开登录页"""
        self.navigate("/#/auth/login")
        self.wait_for_load()
        return self

    @allure.step("登录账号: {account}")
    def login(self, account: str, password: str) -> "LoginPage":
        """执行登录"""
        logger.info(f"登录账号: {account}")
        self.page.fill(self.INPUT_ACCOUNT, account)
        self.page.fill(self.INPUT_PASSWORD, password)
        self.page.click(self.BTN_LOGIN)
        self.page.wait_for_load_state("networkidle")
        return self

    def is_at_login_page(self) -> bool:
        """是否在登录页"""
        return "login" in self.page.url

    def is_login_success(self) -> bool:
        """是否登录成功（离开了登录页）"""
        return not self.is_at_login_page()

    def get_error_message(self) -> str:
        """获取登录错误提示"""
        error_el = self.page.locator('.el-message--error, .ant-message-error')
        if error_el.is_visible():
            return error_el.text_content() or ""
        return ""
