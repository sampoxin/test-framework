import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields

TEST_DATA = load_test_data("test_data.json")

@allure.epic("会员管理")
@allure.feature("会员信息")
class TestMember:
    @allure.story("获取会员信息")
    @pytest.mark.p0
    def test_member_info_get(self, client, context):
        resp = client.send("GET", "/api/v1/wx-mini/member/profile")
        resp_json = resp.json()
        assert resp_json["code"] == "Success"
        assert resp_json["data"]["phone"] == client.user_data["phone"]
        context["memberType"] = resp_json["data"]["typeId"]

    @allure.story("检查会员是否可以更新生日")
    @pytest.mark.p0
    def test_check_birthday_get(self, client, context):
        resp = client.send("GET", "/api/v1/wx-mini/member/checkUpdateBirthday")
        resp_json = resp.json()
        assert resp_json["code"] == "Success"
        context["isCheckBrith"] = resp_json["data"]

    @allure.story("查询会员标签")
    @pytest.mark.p0
    def test_member_tag_get(self, client, context):
        member_type = context.get("memberType")
        if member_type is None:
            pytest.skip("前置用例未生成 member_type")
        resp = client.send("GET", f"/api/v1/wx-mini/member/tag/info/{member_type}")
        assert resp.json()["code"] == "Success"

    @allure.story("更新会员信息")
    @pytest.mark.parametrize("data", TEST_DATA["member_update"], ids=[x["case_name"] for x in TEST_DATA["member_update"]])
    def test_member_update(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST", "/api/v1/wx-mini/member/update",
                          json={"memberId": client.user_data["memberId"], **data_fields})
        assert resp.json()["code"] == data["expected_code"]

    @allure.story("更新会员生日")
    @pytest.mark.parametrize("data", TEST_DATA["member_birthday"], ids=[x["case_name"] for x in TEST_DATA["member_birthday"]])
    def test_member_birthday_put(self, client, context, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST", "/api/v1/wx-mini/member/update",
                          json={"memberId": client.user_data["memberId"], **data_fields})
        resp_json = resp.json()
        is_check = context.get("isCheckBrith")
        assert resp_json["code"] == "Success" if is_check else "MEMBER_MODIFY_BIRTHDAY_YEAR_LIMIT"

    @allure.story("更新会员头像")
    @pytest.mark.parametrize("data", TEST_DATA["member_avatar"], ids=[x["case_name"] for x in TEST_DATA["member_avatar"]])
    def test_member_avatar_put(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST", "/api/v1/wx-mini/member/update",
                          json={"memberId": client.user_data["memberId"], **data_fields})
        assert resp.json()["code"] == data["expected_code"]

    @allure.story("查询乐檬会员卡余额")
    @pytest.mark.p0
    def test_member_lmcard_get(self, client, context):
        resp = client.send("GET", "/api/v1/wx-mini/member/queryLeMengCard")
        resp_json = resp.json()
        assert resp_json["code"] == "Success"
        context["cardUserNum"] = resp_json["data"]["cardUserNum"]

    @allure.story("查询乐檬存款记录")
    @pytest.mark.parametrize("data", TEST_DATA["member_lm_deposit"], ids=[x["case_name"] for x in TEST_DATA["member_lm_deposit"]])
    def test_member_deposit_get(self, client, context, data):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        data_fields = data["request_data"]
        if "cardUserNum" not in data_fields:
            data_fields["cardUserNum"] = card_user_num
        resp = client.send("POST", "/api/v1/wx-mini/member/queryLeMengDeposit", json=data_fields)
        assert resp.json()["code"] == data["expected_code"]

    @allure.story("查询乐檬消费记录")
    @pytest.mark.parametrize("data", TEST_DATA["member_lm_consume"], ids=[x["case_name"] for x in TEST_DATA["member_lm_consume"]])
    def test_member_consume_get(self, client, context, data):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        data_fields = data["request_data"]
        if "cardUserNum" not in data_fields:
            data_fields["cardUserNum"] = card_user_num
        resp = client.send("POST", "/api/v1/wx-mini/member/queryLeMengConsume", json=data_fields)
        assert resp.json()["code"] == data["expected_code"]

    @allure.story("获取微信支付组件token")
    @pytest.mark.p0
    def test_wx_pay_token(self, client):
        resp = client.send("GET", f"/api/v1/wx-mini/member/pay-view/{client.user_data['openId']}")
        assert resp.json()["code"] == "Success"

    @allure.story("查看会员规则")
    @pytest.mark.p0
    def test_member_rule_get(self, client):
        resp = client.send("GET", "/api/v1/wx-mini/member/rule")
        assert resp.json()["code"] == "Success"

    @allure.story("查询会员是否填写完标签")
    @pytest.mark.p0
    def test_member_check_tag(self, client):
        resp = client.send("GET", "/api/v1/wx-mini/member/tag/checkFilled")
        assert resp.json()["code"] == "Success"

    @allure.story("注销会员")
    @pytest.mark.skip(reason="拿不到verifyCode")
    def test_member_cancel(self, client):
        resp = client.send("POST", "/api/v1/wx-mini/member/cancel",
                          json={"memberId": 0, "verifyCode": "string", "isMemberCancel": True})
        assert resp.json()["code"] == "Success"