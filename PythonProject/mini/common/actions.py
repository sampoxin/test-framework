"""
跨页面公共操作
封装可复用的业务流程，供多个测试类调用
"""


def login(mini_test, phone="15973199394"):
    """
    通用登录流程

    Args:
        mini_test: minium.MiniTest 实例
        phone: 手机号
    """
    mini_test.app.redirect_to("/packages/user/login/index")
    page = mini_test.page
    page.get_element(".login-btn").tap()
    page.get_element("input[type='phone']").trigger("input", {"value": phone})
    page.get_element(".confirm-btn").tap()
    page.wait_for(lambda p: p.path == "/pages/home/index")
