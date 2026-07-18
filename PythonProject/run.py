import pytest
import sys
import os

# 切换到 run.py 所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 后端接口测试用例
    test_case_backend = [
        "testcases/backend/"
    ]

    # 小程序测试用例
    test_case_miniapp = [
        "testcases/miniapp/test_personal.py",
        "testcases/miniapp/test_user_info.py"
    ]

    sys.exit(pytest.main([
        *test_case_miniapp,
        "--alluredir=reports/allure-results",
        "-v",
        "--no-cov",
    ]))