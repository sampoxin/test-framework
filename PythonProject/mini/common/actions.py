"""
跨页面公共操作
封装可复用的业务流程，供多个测试类调用
"""
import os
import time
from typing import Optional

from utils.logger import logger
from mini.pages.personal_page import PersonalPage
from mini.pages.login_page import LoginPage


def ensure_logged_in(
    mini_test,
    phone: Optional[str] = None,
    code: Optional[str] = None,
    max_retries: int = 2,
) -> bool:
    """
    判断是否已登录，未登录则自动执行手机号验证码登录

    Args:
        mini_test: minium.MiniTest 实例（pytest 下为 self，仍继承 MiniTest）
        phone: 登录手机号（默认从环境变量 TEST_USER_PHONE 读取）
        code: 验证码（默认从环境变量 TEST_VERIFY_CODE 读取）
        max_retries: 最大重试次数（默认 2）

    Returns:
        bool: 是否已处于登录状态
    """
    # 从环境变量读取凭据（零明文）
    phone = phone or os.environ.get("TEST_USER_PHONE", "")
    code = code or os.environ.get("TEST_VERIFY_CODE", "")
    if not phone:
        logger.warning("[登录] TEST_USER_PHONE 未配置，跳过自动登录")
        return False

    personal_page = PersonalPage(mini_test)
    personal_page.open()

    # 等待个人中心页加载完成（switchTab 后需要时间渲染）
    if not personal_page.wait_for_page(personal_page.PATH, timeout=10):
        logger.warning("个人中心页加载超时")
        return False
    time.sleep(1)

    if personal_page.is_logged_in():
        logger.info("已登录，跳过登录流程")
        return True

    logger.info("未登录，开始自动登录流程")

    # 带重试的登录流程
    last_error: Optional[str] = None
    for attempt in range(1, max_retries + 1):
        try:
            # 尝试点击登录框跳转到登录页
            box = personal_page.login_or_user_box()
            if not box:
                logger.warning("未找到登录框，尝试直接跳转到登录页")
                mini_test.app.redirect_to("/packages/user/login/index")
                time.sleep(2)
            else:
                box.tap()
                time.sleep(2)

            login_page = LoginPage(mini_test)
            if not login_page.is_at_login_page():
                last_error = "未能跳转到登录页"
                logger.warning(f"[登录重试] 第 {attempt}/{max_retries} 次: {last_error}")
                continue

            login_page.switch_to_phone_login()
            time.sleep(1)

            # 验证码为空时仍尝试（可能测试环境不需要验证码）
            result = login_page.login_with_phone(phone, code)
            if result:
                logger.info(f"自动登录成功（第 {attempt} 次尝试）")
                return True
            else:
                last_error = "登录未成功（验证码可能已过期）"
                logger.warning(f"[登录重试] 第 {attempt}/{max_retries} 次: {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"[登录重试] 第 {attempt}/{max_retries} 次异常: {e}")

        # 重试前回到个人中心页
        if attempt < max_retries:
            personal_page.open()
            time.sleep(2)

    logger.warning(f"自动登录 {max_retries} 次重试均失败: {last_error}")
    return False
