import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main([
        "testcases/test_marketing.py",
        "--alluredir=reports/allure-results",
        "-v"
    ]))