"""Web Page Object 基础页面类"""
import os
from typing import List, Optional

import allure
from playwright.sync_api import Locator, Page
from config import ADMIN_URL
from utils.logger import logger


class BasePage:
    """所有页面对象的基类"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.base_url = ADMIN_URL

    @allure.step("导航到 {path}")
    def navigate(self, path: str = "") -> "BasePage":
        """导航到指定路径"""
        url = f"{self.base_url}{path}"
        logger.info(f"导航到: {url}")
        self.page.goto(url)
        return self

    @allure.step("等待页面加载完成")
    def wait_for_load(self) -> "BasePage":
        """等待页面加载完成（networkidle）"""
        self.page.wait_for_load_state("networkidle")
        return self

    @allure.step("等待元素出现: {selector}")
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> Optional[Locator]:
        """等待元素出现"""
        return self.page.wait_for_selector(selector, timeout=timeout)

    @allure.step("截图: {name}")
    def screenshot(self, name: str = "screenshot") -> str:
        """截图"""
        os.makedirs("reports/screenshots", exist_ok=True)
        path = f"reports/screenshots/{name}.png"
        self.page.screenshot(path=path)
        logger.info(f"截图已保存: {path}")
        return path

    def is_visible(self, selector: str) -> bool:
        """元素是否可见"""
        return self.page.locator(selector).is_visible()

    def get_text(self, selector: str, text: Optional[str] = None) -> str:
        """获取元素文本（inner_text）"""
        try:
            return self.find_element(selector, text).inner_text()
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return ""

    def get_text_content(self, selector: str, text: Optional[str] = None) -> str:
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

    def find_element(self, selector: str, text: Optional[str] = None) -> Locator:
        """获取元素定位器"""
        return self.page.locator(selector, has_text=text)

    def find_element_by_label(self, label: str) -> Locator:
        """根据标签获取元素定位器"""
        return self.page.get_by_label(label)

    def find_elements(self, selector: str) -> List[Locator]:
        """获取所有匹配的元素列表"""
        return self.page.locator(selector).all()

    @allure.step("点击元素: {selector}")
    def click_element(self, selector: str, text: Optional[str] = None) -> None:
        """点击元素"""
        try:
            self.find_element(selector, text).click()
        except Exception as e:
            logger.error(f"点击元素: {selector}，文本为: {text} 失败: {e}")
            raise

    @allure.step("填写输入框: {selector}")
    def fill_input(self, selector: str, value: str) -> None:
        """填写输入框"""
        self.page.fill(selector, value)
