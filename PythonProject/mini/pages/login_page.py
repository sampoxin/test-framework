"""
登录页 Page Object
封装登录页的元素定位和操作，供测试用例调用
"""
import time
from typing import Any, Optional

import allure
from utils.logger import logger
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页"""
    PATH = "/packages/user/login/index"
    QUICK_LOGIN_BTN = "#agree-btn"
    WELCOME_VIDEO = "#welcomeVideo"
    AGREEMENT_CHECKBOX = ".nut-checkbox"

    def __init__(self, mini_test: Any) -> None:
        """
        Args:
            mini_test: minium.MiniTest 实例，提供 self.page / self.app
        """
        self.mini = mini_test

    @property
    def page(self) -> Any:
        return self.mini.page

    @allure.step("打开登录页")
    def open(self) -> "LoginPage":
        """跳转到登录页"""
        self.navigate_to(self.PATH)
        return self

    @allure.step("返回上一页")
    def to_back(self) -> "LoginPage":
        """返回上一页"""
        self.go_back()
        return self

    # ========== 页面判断 ==========

    def is_at_login_page(self) -> bool:
        """是否在登录页"""
        return "login" in self.get_page_path()

    def is_quick_mode(self) -> bool:
        """是否为一键登录模式（默认模式）"""
        return self.find_element(self.QUICK_LOGIN_BTN, max_timeout=5) is not None

    def is_phone_mode(self) -> bool:
        """是否为手机号登录模式"""
        try:
            inputs = self.find_elements("input", max_timeout=2)
            return inputs is not None and len(inputs) > 0
        except Exception:
            return False

    def has_phone_input(self) -> bool:
        """手机号输入框是否存在"""
        try:
            inputs = self.find_elements("input", max_timeout=2)
            if inputs:
                for inp in inputs:
                    placeholder = inp.attribute("placeholder") or ""
                    if "手机号" in placeholder:
                        return True
                return len(inputs) > 0
            return False
        except Exception:
            return False

    # ========== 视频相关 ==========

    def has_video(self) -> bool:
        """欢迎视频是否存在"""
        return self.find_element(self.WELCOME_VIDEO, max_timeout=5) is not None

    # ========== 登录模式切换 ==========

    @allure.step("切换到手机号登录模式")
    def switch_to_phone_login(self) -> "LoginPage":
        """切换到手机号登录模式"""
        self.tap("button", inner_text="手机号安全登录")
        return self

    @allure.step("手机号登录: {phone}")
    def login_with_phone(self, phone: str, code: str, agree: bool = True) -> bool:
        """
        完整流程：手机号验证码登录
        :param phone: 手机号
        :param code: 验证码
        :param agree: 是否勾选协议（默认 True）
        :return: 是否登录成功
        """
        self.fill_phone_form(phone, code)
        if agree:
            self.agree_and_submit_phone()
        else:
            self.tap_phone_login_submit()
            time.sleep(2)
        success = self.is_login_success()
        logger.info(f"[流程] 手机号登录结果: {'成功' if success else '失败'}")
        return success

    @allure.step("填写手机号登录表单")
    def fill_phone_form(self, phone: str, code: str) -> "LoginPage":
        """
        子流程：填写手机号登录表单
        前置条件：已切换到手机号登录模式

        :param phone: 手机号
        :param code: 验证码
        """
        self.input_phone(phone)
        self.tap_send_code()
        time.sleep(2)  # 等待验证码发送（服务端处理需要时间）
        self.input_verify_code(code)
        time.sleep(0.5)  # 等待输入框失焦
        return self

    # ========== 手机号登录操作 ==========

    @allure.step("输入手机号")
    def input_phone(self, phone: str) -> "LoginPage":
        """输入手机号（需先切换到手机号模式）"""
        logger.info(f"输入手机号: {phone[:3]}****{phone[-4:]}")
        try:
            inputs = self.page.get_elements("input", max_timeout=3)
            for inp in inputs:
                placeholder = inp.attribute("placeholder") or ""
                if "手机号" in placeholder:
                    inp.input(phone)
                    return self
            # 兜底：取第一个 input
            if inputs:
                inputs[0].input(phone)
        except Exception as e:
            logger.error(f"输入手机号失败: {e}")
        return self

    @allure.step("输入验证码")
    def input_verify_code(self, code: str) -> "LoginPage":
        """输入验证码（需先切换到手机号模式）"""
        logger.info("输入验证码")
        try:
            inputs = self.find_elements("input", max_timeout=3)
            if inputs:
                for inp in inputs:
                    placeholder = inp.attribute("placeholder") or ""
                    if "验证码" in placeholder:
                        inp.input(code)
                        return self
                # 兜底：取第二个 input
                if len(inputs) >= 2:
                    inputs[1].input(code)
        except Exception as e:
            logger.error(f"输入验证码失败: {e}")
        return self

    @allure.step("点击获取验证码")
    def tap_send_code(self) -> "LoginPage":
        """点击获取验证码按钮"""
        logger.info("点击获取验证码")
        try:
            self.tap("text", inner_text="获取验证码")
        except Exception:
            try:
                self.tap("view", inner_text="获取验证码")
            except Exception as e:
                logger.warning(f"点击获取验证码失败: {e}")
        return self

    @allure.step("勾选协议并提交登录")
    def agree_and_submit_phone(self) -> "LoginPage":
        """
        子流程：勾选协议 + 提交手机号登录
        前置条件：已填写手机号和验证码
        """
        self.check_agreement()
        self.tap_phone_login_submit()
        time.sleep(2)  # 等待登录请求完成
        return self

    # ========== 协议勾选 ==========

    def check_agreement(self) -> "LoginPage":
        """勾选协议"""
        logger.info("勾选协议")
        self.tap(self.AGREEMENT_CHECKBOX)
        time.sleep(0.5)  # 等待勾选动画
        return self

    def tap_phone_login_submit(self) -> "LoginPage":
        """点击手机号登录提交按钮"""
        logger.info("点击手机号登录提交")
        try:
            self.tap("button", inner_text="登录")
        except Exception as e:
            logger.warning(f"点击手机号登录提交失败: {e}")
        return self

    # ========== 状态判断 ==========

    def is_login_success(self) -> bool:
        """是否登录成功（离开登录页）"""
        time.sleep(2)  # 等待登录响应和页面跳转
        return not self.is_at_login_page()
