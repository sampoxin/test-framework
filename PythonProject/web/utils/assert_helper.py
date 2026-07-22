"""断言辅助工具：区分元素缺失和其他错误"""
from playwright.sync_api import Page, expect as pw_expect
from utils.logger import logger


class ElementNotFoundError(Exception):
    """元素找不到错误"""
    pass


class AssertHelper:
    """
    断言辅助类

    用法：
        ah = AssertHelper(page)
        ah.assert_visible("请输入账号", by="placeholder")  # 元素可见
        ah.assert_text_equals("欢迎登录", "欢迎登录")       # 文本匹配
        ah.assert_url_contains("/home")                    # URL 包含
        ah.assert_true(login_page.is_login_success(), "登录应成功")  # 逻辑断言
    """

    def __init__(self, page: Page):
        self.page = page

    # ========== 元素断言（找不到 → ElementNotFoundError） ==========

    def assert_visible(self, selector_desc: str, by: str = "text",
                       timeout: int = 5000) -> "AssertHelper":
        """
        断言元素可见，找不到则抛出 ElementNotFoundError

        :param selector_desc: 选择器描述（文本/placeholder/role名等）
        :param by: 定位方式 text / placeholder / role / test_id / css
        :param timeout: 超时毫秒
        """
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_be_visible(timeout=timeout)
        except Exception as e:
            msg = f"[元素缺失] 找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    def assert_hidden(self, selector_desc: str, by: str = "text",
                      timeout: int = 5000) -> "AssertHelper":
        """断言元素不可见"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_be_hidden(timeout=timeout)
        except Exception as e:
            msg = f"[元素缺失] 断言隐藏时找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    def assert_text_equals(self, selector_desc: str, expected: str,
                           by: str = "text") -> "AssertHelper":
        """
        断言元素文本等于期望値

        找不到元素 → ElementNotFoundError
        文本不匹配 → AssertionError
        """
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_have_text(expected)
        except AssertionError:
            actual = ""
            try:
                actual = locator.inner_text()
            except Exception:
                pass
            msg = f"[断言失败] 文本不匹配: expected='{expected}', actual='{actual}'"
            logger.warning(msg)
            raise AssertionError(msg)
        except Exception as e:
            msg = f"[元素缺失] 找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    def assert_text_contains(self, selector_desc: str, expected: str,
                             by: str = "text") -> "AssertHelper":
        """断言元素文本包含期望値"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_contain_text(expected)
        except AssertionError:
            actual = ""
            try:
                actual = locator.inner_text()
            except Exception:
                pass
            msg = f"[断言失败] 文本不包含: expected包含='{expected}', actual='{actual}'"
            logger.warning(msg)
            raise AssertionError(msg)
        except Exception as e:
            msg = f"[元素缺失] 找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    def assert_element_count(self, selector_desc: str, expected_count: int,
                             by: str = "css") -> "AssertHelper":
        """断言元素数量"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_have_count(expected_count)
        except Exception as e:
            msg = f"[元素缺失] 找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    def assert_has_value(self, selector_desc: str, expected: str,
                         by: str = "placeholder") -> "AssertHelper":
        """断言输入框的値"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_have_value(expected)
        except Exception as e:
            msg = f"[元素缺失] 找不到元素: by={by}, selector={selector_desc}"
            logger.error(msg)
            raise ElementNotFoundError(msg) from e
        return self

    # ========== 逻辑断言（非元素缺失 → AssertionError） ==========

    def assert_true(self, condition: bool, message: str = "") -> "AssertHelper":
        """断言条件为 True"""
        if not condition:
            msg = f"[断言失败] {message}"
            logger.warning(msg)
            raise AssertionError(msg)
        return self

    def assert_false(self, condition: bool, message: str = "") -> "AssertHelper":
        """断言条件为 False"""
        if condition:
            msg = f"[断言失败] {message}"
            logger.warning(msg)
            raise AssertionError(msg)
        return self

    def assert_url_contains(self, url_pattern: str) -> "AssertHelper":
        """断言当前 URL 包含指定字符串"""
        if url_pattern not in self.page.url:
            msg = f"[断言失败] URL 不匹配: 期望包含 '{url_pattern}', 实际='{self.page.url}'"
            logger.warning(msg)
            raise AssertionError(msg)
        return self

    def assert_equals(self, actual, expected, message: str = "") -> "AssertHelper":
        """断言相等"""
        if actual != expected:
            msg = f"[断言失败] {message}: expected={expected}, actual={actual}"
            logger.warning(msg)
            raise AssertionError(msg)
        return self

    def assert_not_equals(self, actual, expected, message: str = "") -> "AssertHelper":
        """断言不等"""
        if actual == expected:
            msg = f"[断言失败] {message}: 不应等于 {expected}"
            logger.warning(msg)
            raise AssertionError(msg)
        return self

    # ========== 内部方法 ==========

    def _resolve_locator(self, desc: str, by: str):
        """根据定位方式返回 Playwright Locator"""
        if by == "text":
            return self.page.get_by_text(desc)
        elif by == "placeholder":
            return self.page.get_by_placeholder(desc)
        elif by == "role":
            # desc 格式: "button,登录" → role=button, name=登录
            if "," in desc:
                role, name = desc.split(",", 1)
                return self.page.get_by_role(role.strip(), name=name.strip())
            return self.page.get_by_role(desc)
        elif by == "test_id":
            return self.page.get_by_test_id(desc)
        elif by == "label":
            return self.page.get_by_label(desc)
        elif by == "css":
            return self.page.locator(desc)
        else:
            return self.page.get_by_text(desc)
