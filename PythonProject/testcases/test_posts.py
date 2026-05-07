import json
import allure
import pytest


def load_test_data():
    with open("data/test_data.json", encoding="utf-8") as f:
        return json.load(f)

@allure.epic("文章管理")
@allure.feature("文章 CRUD")
@allure.story("获取/创建文章")
@pytest.mark.parametrize("test_data", load_test_data(), ids=lambda x: x["case_name"])
def test_posts(client,test_data):
    request_data = test_data.get("request_data",{})
    with allure.step("发送请求"):
        # **解包
        result = client.send(test_data["method"], test_data["url"], **request_data)
    with allure.step("验证状态码"):
        assert result.status_code == test_data["expected_status"]

    if test_data["method"] == "POST":
        with allure.step("验证响应体中的 title 字段"):
            assert result.json()["title"] == "hello"

    if test_data["method"] == "GET" and test_data["url"] == "/posts":
        with allure.step("验证返回列表长度"):
            assert len(result.json()) == 100