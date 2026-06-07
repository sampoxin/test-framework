import pytest
import sys
import os

# 切换到 run.py 所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    sys.exit(pytest.main([
        "testcases/test_coupon.py",
        "--alluredir=reports/allure-results",
        "-v"
    ]))