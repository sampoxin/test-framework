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
        """判断元素是否可见

        minium 元素没有 is_visible() 方法，这里通过计算样式 + 尺寸判断：
        - display != none 且 visibility != hidden 且 opacity != 0
        - 宽高均大于 0
        """
        element = self.find_element(selector, inner_text)
        if element is None:
            return False
        try:
            display, visibility, opacity = element.styles(["display", "visibility", "opacity"])
            if display == "none" or visibility == "hidden":
                return False
            if opacity not in (None, "") and float(opacity) == 0:
                return False
        except Exception as e:
            logger.warning(f"获取元素样式失败，降级为尺寸判断: {e}")
        try:
            size = element.size
            return size.width > 0 and size.height > 0
        except Exception as e:
            logger.warning(f"获取元素尺寸失败: {e}")
            return True  # 元素存在但取不到尺寸，视为可见

    def is_enabled(self, selector: str, inner_text: Optional[str] = None) -> bool:
        """判断元素是否可点击（minium 无 is_enabled()，通过 disabled 属性判断）"""
        element = self.find_element(selector, inner_text)
        if element is None:
            return False
        try:
            disabled = element.attribute("disabled")
            if isinstance(disabled, (list, tuple)):
                disabled = disabled[0] if disabled else None
            return str(disabled).lower() not in ("true", "disabled")
        except Exception:
            return True  # 无 disabled 属性视为可用

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
        """滚动使元素可见

        minium 没有 scroll_into_view() 方法，这里根据元素类型做兼容：
        - scroll-view 元素：调用 element.scroll_to(0, 0) 触发其父级滚动
        - 普通元素：通过 call_func 执行 element.scrollIntoView({block:'center'})
        若上述均失败，则作为兜底不做任何操作（由用例层保证）
        """
        element = self.find_element(selector, inner_text)
        if element is None:
            return self

        # 优先尝试调用原生 scrollIntoView
        try:
            element.call_func("scrollIntoView", [{"block": "center"}])
            time.sleep(0.5)
            return self
        except Exception as e:
            logger.warning(f"call_func scrollIntoView 失败，降级为 scroll_to: {e}")

        # 降级：scroll-view 直接调 scroll_to
        try:
            if getattr(element, "_tag_name", "") == "scroll-view":
                element.scroll_to(0, 0)
            else:
                element.scroll_to(0, 0)
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"scroll_to 兜底失败: {e}")
        return self
