import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main([
        "testcases/test_coupon.py",
        "--alluredir=reports/allure-results",
        "-v"
    ]))