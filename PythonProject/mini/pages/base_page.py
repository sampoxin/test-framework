"""小程序 Page Object 基础页面类"""
import time
from typing import Any, List, Optional

import allure
from utils.logger import logger


class BasePage:
    """所有小程序页面对象的基类"""

    def __init__(self, mini: Any) -> None:
        self.mini = mini
        self.page = mini.page
        self.app = mini.app

    # ========== 页面跳转 ==========

    @allure.step("切换Tab: {url}")
    def switch_tab(self, url: str) -> "BasePage":
        """切换tab"""
        self.mini.app.switch_tab(url)
        return self

    @allure.step("重定向到: {url}")
    def redirect_to(self, url: str) -> "BasePage":
        """不需要返回的跳转"""
        self.mini.app.redirect_to(url)
        return self

    @allure.step("导航到: {url}")
    def navigate_to(self, url: str) -> "BasePage":
        """需要返回的跳转"""
        self.mini.app.navigate_to(url)
        return self

    @allure.step("返回上一页")
    def go_back(self) -> "BasePage":
        """返回上一页"""
        self.mini.app.navigate_back()
        return self

    # ========== 页面元素 ==========

    def find_element(self, selector: str, inner_text: Optional[str] = None,
                     max_timeout: int = 3) -> Optional[Any]:
        """根据元素描述符查找单个元素"""
        try:
            element = self.page.get_element(selector, inner_text=inner_text, max_timeout=max_timeout)
            logger.info(f"找到元素: {selector} {inner_text}")
            return element
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            return None

    def find_elements(self, selector: str, inner_text: Optional[str] = None,
                      max_timeout: int = 3) -> Optional[List[Any]]:
        """根据元素描述符查找多个元素"""
        try:
            elements = self.page.get_elements(selector, inner_text=inner_text, max_timeout=max_timeout)
            logger.info(f"找到元素: {selector} {inner_text}")
            return elements
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            return None

    # ========== 页面元素操作 ==========

    @allure.step("点击: {selector}")
    def tap(self, selector: str, inner_text: Optional[str] = None) -> "BasePage":
        """点击元素"""
        element = self.find_element(selector, inner_text)
        if element:
            element.tap()
        return self

    @allure.step("输入: {selector} = {text}")
    def input(self, selector: str, inner_text: Optional[str] = None, text: str = "") -> "BasePage":
        """输入文本"""
        element = self.find_element(selector, inner_text)
        if element:
            element.input(text)
        return self

    def get_text(self, selector: str, inner_text: Optional[str] = None) -> str:
        """获取元素文本"""
        element = self.find_element(selector, inner_text)
        if element:
            return element.text
        return ""

    def get_attribute(self, selector: str, inner_text: Optional[str] = None,
                      attribute: str = "") -> str:
        """获取元素属性"""
        element = self.find_element(selector, inner_text)
        if element:
            return element.attribute(attribute)
        return ""

    def get_value(self, selector: str, inner_text: Optional[str] = None) -> str:
        """获取value元素属性"""
        return self.get_attribute(selector, inner_text, "value")

    # ========== 页面元素判断 ==========

    def is_visible(self, selector: str, inner_text: Optional[str] = None) -> bool:
        """判断元素是否可见"""
        element = self.find_element(selector, inner_text)
        return element is not None and element.is_visible()

    def is_enabled(self, selector: str, inner_text: Optional[str] = None) -> bool:
        """判断元素是否可点击"""
        element = self.find_element(selector, inner_text)
        return element is not None and element.is_enabled()

    def is_exists(self, selector: str, inner_text: Optional[str] = None) -> bool:
        """判断元素是否存在"""
        element = self.find_element(selector, inner_text)
        return element is not None

    def get_page_path(self) -> str:
        """获取当前页面路径"""
        return self.page.path

    def get_page_title(self) -> str:
        """获取当前页面标题"""
        return self.page.title

    @allure.step("等待页面: {path}")
    def wait_for_page(self, path: str, timeout: int = 10) -> bool:
        """等待页面加载"""
        start = time.time()
        while time.time() - start < timeout:
            if self.page.path == path:
                return True
            time.sleep(0.5)
        return False

    def wait_for_element(self, selector: str, timeout: int = 5) -> bool:
        """等待元素加载"""
        try:
            self.page.wait_for(selector, max_timeout=timeout)
            logger.info(f"元素加载成功: {selector} ")
            return True
        except Exception as e:
            logger.error(f"元素加载失败: {e}")
            return False

    @allure.step("滚动到元素: {selector}")
    def scroll_to_view(self, selector: str, inner_text: Optional[str] = None) -> "BasePage":
        """滚动到元素可见"""
        element = self.find_element(selector, inner_text)
        if element:
            element.scroll_into_view()
        return self
