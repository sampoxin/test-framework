"""
跨页面公共操作
封装可复用的业务流程，供多个测试类调用
"""
import time
from utils.logger import logger
from mini.pages.personal_page import PersonalPage
from mini.pages.login_page import LoginPage


def ensure_logged_in(mini_test, phone="15973199394", code="912391"):
    """
    判断是否已登录，未登录则自动执行手机号验证码登录

    Args:
        mini_test: minium.MiniTest 实例（pytest 下为 self，仍继承 MiniTest）
        phone: 登录手机号
        code: 验证码

    Returns:
        bool: 是否已处于登录状态
    """
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
        logger.warning("未能跳转到登录页")
        return False

    login_page.switch_to_phone_login()
    time.sleep(1)
    result = login_page.login_with_phone(phone, code)
    if result:
        logger.info("自动登录成功")
    else:
        logger.warning("自动登录失败（验证码可能已过期）")
    return result
