import pytest
import sys
import os

# 切换到 run.py 所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 解析命令行参数，支持选择性运行
    # 用法：
    #   python run.py                    # 运行全部用例（backend + miniapp + web）
    #   python run.py web                # 仅运行后台管理系统UI测试
    #   python run.py web --slowmo=0     # Web 测试关闭慢速（CI 模式）
    #   python run.py web --slowmo=500   # Web 测试加大延迟（调试观察）
    #   python run.py backend            # 仅运行后端接口测试
    #   python run.py backend --api-think-time=500  # API 请求后等待 500 毫秒
    #   python run.py miniapp            # 仅运行小程序UI测试
    #   python run.py mini_client        # 仅运行小程序接口测试
    #
    # 注意：--slowmo 默认配置在 testcases/web/conftest.py 中（默认 1000ms），
    #       命令行传 --slowmo=N 可覆盖默认值；
    #       --api-think-time 用于控制纯 API 测试的请求后等待时间（单位毫秒，默认 0）。
    args = sys.argv[1:]

    # 分离测试类型选择器和 pytest 透传参数（以 - 开头的参数透传给 pytest）
    TEST_TYPES = {"web", "miniapp", "backend", "mini_client"}
    passthrough_args = [a for a in args if a.startswith("-")]

    # 后台管理系统 UI 测试用例
    test_case_web = ["testcases/web/test_receipt_invoice.py"]

    # 后端接口测试用例
    test_case_backend = [
        "testcases/backend/"
    ]

    # 小程序UI测试用例
    test_case_miniapp = [
        "testcases/miniapp/test_takeout.py"
    ]
    # 小程序接口测试用例
    test_case_mini_client = [
        "testcases/mini_client/test_member.py",
    ]

    if "web" in args:
        test_case = test_case_web
    elif "miniapp" in args:
        test_case = test_case_miniapp
    elif "backend" in args:
        test_case = test_case_backend
    elif "mini_client" in args:
        test_case = test_case_mini_client
    else:
        test_case = test_case_backend + test_case_miniapp + test_case_web + test_case_mini_client

    pytest_args = [
        *test_case,
        "--alluredir=reports/allure-results",
        "-v",
        *passthrough_args,   # 透传用户指定的 pytest 参数（如 --slowmo=0）
    ]

    # 小程序测试包含 minium 线程，需禁用 coverage 避免卡死
    if any(p in test_case for p in test_case_miniapp):
        pytest_args.append("--no-cov")

    sys.exit(pytest.main(pytest_args))
