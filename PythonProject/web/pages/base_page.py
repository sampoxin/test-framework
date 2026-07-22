"""Web Page Object 基础页面类"""
import os
from playwright.sync_api import Page
from config import ADMIN_URL
from utils.logger import logger


class BasePage:
    """所有页面对象的基类"""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = ADMIN_URL

    def navigate(self, path: str = ""):
        """导航到指定路径"""
        url = f"{self.base_url}{path}"
        logger.info(f"导航到: {url}")
        self.page.goto(url)

    def wait_for_load(self):
        """等待页面加载完成（networkidle）"""
        self.page.wait_for_load_state("networkidle")

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """等待元素出现"""
        self.page.wait_for_selector(selector, timeout=timeout)

    def screenshot(self, name: str = "screenshot"):
        """截图"""
        os.makedirs("reports/screenshots", exist_ok=True)
        path = f"reports/screenshots/{name}.png"
        self.page.screenshot(path=path)
        logger.info(f"截图已保存: {path}")
        return path

    def is_visible(self, selector: str) -> bool:
        """元素是否可见"""
        return self.page.locator(selector).is_visible()

    def get_text(self, selector: str, text=None) -> str:
        """获取元素文本（inner_text）"""
        try:
            return self.find_element(selector, text).inner_text()
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return ""

    def get_text_content(self, selector: str, text=None) -> str:
        """获取元素文本内容（text_content，包含隐藏文本）"""
        try:
            return self.find_element(selector, text).text_content() or ""
        except Exception as e:
            logger.error(f"获取元素文本内容失败: {e}")
            return ""

    def get_input_value(self, selector: str) -> str:
        """获取输入框的值"""
        try:
            return self.find_element(selector).input_value()
        except Exception as e:
            logger.error(f"获取输入框值失败: {e}")
            return ""

    def find_element(self, selector: str, text=None) -> object:
        """获取元素定位器"""
        return self.page.locator(selector, has_text=text)

    def find_element_by_label(self, label: str) -> object:
        """根据标签获取元素定位器"""
        return self.page.get_by_label(label)

    def find_elements(self, selector: str) -> list:
        """获取所有匹配的元素列表"""
        return self.page.locator(selector).all()

    def click_element(self, selector: str, text=None):
        """点击元素"""
        try:
            self.find_element(selector, text).click()
        except Exception as e:
            logger.error(f"点击元素: {selector}，文本为: {text} 失败: {e}")
            raise

    def fill_input(self, selector: str, value: str):
        """填写输入框"""
        self.page.fill(selector, value)
