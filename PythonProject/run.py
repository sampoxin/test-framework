import pytest
import sys
import os

# 切换到 run.py 所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    test_case = [
        "testcases/backend/"
    ]
    sys.exit(pytest.main([
        *test_case,
        "--alluredir=reports/allure-results",
        "-v"
    ]))