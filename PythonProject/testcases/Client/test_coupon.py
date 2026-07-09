import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields

TEST_DATA = load_test_data("test_data.json")

@allure.epic("优惠券模块")
@allure.feature("优惠券功能")
class TestCoupon:
    @allure.story("获取用户优惠券数量")
    def test_coupon_count(self, client):
        resp = client.send("POST", "/api/v1/wx-mini/coupon/countUserCoupons", json={"statusList": [2]})
        resp_json = resp.json()
        assert resp_json["code"] == "Success"

    @allure.story("优惠券")
    @pytest.mark.parametrize("data", TEST_DATA["coupon_list"], ids=[x["case_name"] for x in TEST_DATA["coupon_list"]])
    def test_coupon_list(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        with allure.step("获取优惠券列表"):
            resp = client.send("POST", "/api/v1/wx-mini/coupon/list", json=data_fields)
            resp_json = resp.json()
            assert resp_json["code"] == data["expected_code"]
        
        if resp_json.get("data") and resp_json["data"].get("total",0) > 0:
            data_list = resp_json["data"].get("data", [])
            coupon_id = data_list[0]["id"]
            template_id = data_list[0]["templateId"]
            with allure.step("查看优惠券详情"):
                resp_detail = client.send("POST", "/api/v1/wx-mini/coupon/details", json={"id": coupon_id})
                assert resp_detail.json()["code"] == "Success"
        
            with allure.step("查询用户优惠券城市列表"):
                resp_template = client.send("POST", "/api/v1/wx-mini/coupon/cityList", json={"templateId": template_id})
                resp_template_json = resp_template.json()
                assert resp_template_json["code"] == "Success"

            if resp_template_json.get("data") and resp_template_json["data"].get("data"):
                city_list = resp_template_json["data"].get("data", [])
                with allure.step("查询用户优惠券门店列表"):
                    resp_store = client.send("POST", "/api/v1/wx-mini/coupon/storeList", json={"templateId": template_id, "cityCode": city_list[0]["cityCode"]})
                    resp_store_json = resp_store.json()
                    assert resp_store_json["code"] == "Success"

            with allure.step("查询用户优惠券适用商品"):
                resp_store = client.send("POST", "/api/v1/wx-mini/coupon/goodsScope", json={"templateId": template_id})
                assert resp_store.json()["code"] == "Success"
            


