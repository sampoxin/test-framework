"""断言辅助工具：区分元素缺失和其他错误"""
import allure
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
        ah.assert_toast("操作成功")                        # Toast 消息断言
        ah.assert_enabled("确 定", by="text")               # 控件可用
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    # ========== 元素断言（找不到 → ElementNotFoundError） ==========

    @allure.step("断言元素可见: {selector_desc}")
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

    @allure.step("断言元素隐藏: {selector_desc}")
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

    @allure.step("断言文本等于: expected='{expected}'")
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

    @allure.step("断言文本包含: expected='{expected}'")
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

    # ========== Toast / Message 断言 ==========

    @allure.step("断言 Toast 消息: expected='{expected}'")
    def assert_toast(self, expected: str, toast_type: str = "",
                     timeout: int = 5000) -> "AssertHelper":
        """
        断言 Toast/Message 消息内容

        :param expected: 期望的 Toast 文本内容（部分匹配）
        :param toast_type: 类型过滤 success/error/warning/info（可选）
        :param timeout: 超时毫秒
        """
        # Ant Design Message 通用选择器
        selectors = [".ant-message-notice-content", ".ant-message-custom-content"]
        if toast_type:
            selectors = [f".ant-message-{toast_type}"]

        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                if locator.is_visible(timeout=timeout):
                    actual = locator.text_content() or ""
                    if expected in actual:
                        logger.info(f"[Toast] 断言通过: '{expected}' 包含于 '{actual}'")
                        return self
            except Exception:
                continue

        # 兜底：搜索所有可见的 message 元素
        all_messages = self.page.locator(".ant-message-notice").all()
        collected = []
        for msg in all_messages:
            try:
                text = msg.text_content() or ""
                collected.append(text)
                if expected in text:
                    logger.info(f"[Toast] 断言通过: '{expected}' 包含于 '{text}'")
                    return self
            except Exception:
                continue

        msg = f"[断言失败] 未找到匹配的 Toast 消息: expected='{expected}', 当前消息={collected}"
        logger.warning(msg)
        raise AssertionError(msg)

    @allure.step("断言 Toast 成功: '{expected}'")
    def assert_toast_success(self, expected: str = "", timeout: int = 5000) -> "AssertHelper":
        """断言成功类型 Toast（绿色提示）"""
        return self.assert_toast(expected, toast_type="success", timeout=timeout)

    @allure.step("断言 Toast 错误: '{expected}'")
    def assert_toast_error(self, expected: str = "", timeout: int = 5000) -> "AssertHelper":
        """断言错误类型 Toast（红色提示）"""
        return self.assert_toast(expected, toast_type="error", timeout=timeout)

    # ========== 控件状态断言 ==========

    @allure.step("断言控件可用: {selector_desc}")
    def assert_enabled(self, selector_desc: str, by: str = "text",
                       timeout: int = 5000) -> "AssertHelper":
        """断言控件处于可用（enabled）状态"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_be_enabled(timeout=timeout)
        except Exception as e:
            msg = f"[断言失败] 控件不可用: by={by}, selector={selector_desc}"
            logger.warning(msg)
            raise AssertionError(msg) from e
        return self

    @allure.step("断言控件禁用: {selector_desc}")
    def assert_disabled(self, selector_desc: str, by: str = "text",
                      timeout: int = 5000) -> "AssertHelper":
        """断言控件处于禁用（disabled）状态"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_be_disabled(timeout=timeout)
        except Exception as e:
            msg = f"[断言失败] 控件未禁用: by={by}, selector={selector_desc}"
            logger.warning(msg)
            raise AssertionError(msg) from e
        return self

    @allure.step("断言复选框选中: {selector_desc}")
    def assert_checked(self, selector_desc: str, by: str = "css",
                       timeout: int = 5000) -> "AssertHelper":
        """断言复选框/开关处于选中状态"""
        locator = self._resolve_locator(selector_desc, by)
        try:
            pw_expect(locator).to_be_checked(timeout=timeout)
        except Exception as e:
            msg = f"[断言失败] 控件未选中: by={by}, selector={selector_desc}"
            logger.warning(msg)
            raise AssertionError(msg) from e
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

    @allure.step("断言 URL 包含: '{url_pattern}'")
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
