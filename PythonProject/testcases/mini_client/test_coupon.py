import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields

TEST_DATA = load_test_data("test_data.json")


@allure.epic("优惠券模块")
@allure.feature("优惠券功能")
class TestCoupon:

    @allure.story("获取用户优惠券数量")
    def test_coupon_count(self, coupon_api):
        coupon_api.count_user_coupons(status_list=[2])

    @allure.story("优惠券")
    @pytest.mark.parametrize("data", TEST_DATA["coupon_list"],
                             ids=[x["case_name"] for x in TEST_DATA["coupon_list"]])
    def test_coupon_list(self, coupon_api, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        with allure.step("获取优惠券列表"):
            result = coupon_api.list_coupons(**data_fields)
            assert result["code"] == data["expected_code"]

        if result.get("data") and result["data"].get("total", 0) > 0:
            data_list = result["data"].get("data", [])
            coupon_id = data_list[0]["id"]
            template_id = data_list[0]["templateId"]

            with allure.step("查看优惠券详情"):
                coupon_api.get_details(coupon_id)

            with allure.step("查询用户优惠券城市列表"):
                city_result = coupon_api.get_city_list(template_id)
                if city_result.get("data") and city_result["data"].get("data"):
                    city_list = city_result["data"]["data"]

                    with allure.step("查询用户优惠券门店列表"):
                        coupon_api.get_store_list(template_id, city_list[0]["cityCode"])

            with allure.step("查询用户优惠券适用商品"):
                coupon_api.get_goods_scope(template_id)
