import allure
import pytest
from utils.tools import get_img, load_test_data, resolve_dynamic_fields



@allure.epic("会员管理")
@allure.feature("会员信息")
class TestMember:
    @allure.story("获取会员信息")
    def test_member_info_get(self,client,context):
        resp = client.send("GET",
                       "/api/v1/wx-mini/member/profile"
                       )
        resp_json = resp.json()
        assert resp_json["msg"]=="成功"
        assert resp_json["data"]["phone"] == client.user_data["phone"]
        context["memberType"] = resp_json["data"]["typeId"]

    @allure.story("检查会员是否可以更新生日")
    def test_check_birthday_get(self, client,context):
        resp = client.send("GET",
                           "/api/v1/wx-mini/member/checkUpdateBirthday"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"
        context["isCheckBrith"] = resp_json["data"]

    @allure.story("查询会员标签")
    @pytest.mark.skip
    def test_member_tag_get(self, client,context):
        member_type = context.get("memberType")
        if member_type is None:
            pytest.skip("前置用例未生成 member_type")
        resp = client.send("GET",
                           f"/api/v1/wx-mini/member/tag/info/{member_type}"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    member_update_data = load_test_data("test_data.json")["member_update"]
    @allure.story("更新会员信息")
    @pytest.mark.parametrize("data", member_update_data,ids=[x["case_name"] for x in member_update_data])
    def test_member_name_put(self, client, data):
        user_data = client.user_data
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST",
                       "/api/v1/wx-mini/member/update",
                       json={
                            "memberId": user_data["memberId"],
                            **data_fields
                       })
        resp_json = resp.json()
        assert resp_json["msg"] == data["expected_msg"]

    member_birthday_data = load_test_data("test_data.json")["member_birthday"]
    @allure.story("更新会员生日")
    @pytest.mark.parametrize("data", member_birthday_data,ids=[x["case_name"] for x in member_birthday_data])
    def test_member_birthday_put(self, client,context,data):
        user_data = client.user_data
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST",
                       "/api/v1/wx-mini/member/update",
                       json={
                            "memberId": user_data["memberId"],
                            **data_fields
                       })
        resp_json = resp.json()
        is_check = context.get("isCheckBrith")
        assert resp_json["msg"] == "成功" if is_check else "失败"

    @allure.story("更新会员头像")
    def test_member_avatar_put(self, client):
        user_data = client.user_data
        resp = client.send("POST",
                       "/api/v1/wx-mini/member/update",
                       json={
                            "memberId": user_data["memberId"],
                            "avatar": get_img()
                       })
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    @allure.story("查询乐檬会员卡余额")
    def test_member_lmcard_get(self, client,context):
        resp = client.send("GET",
                           "/api/v1/wx-mini/member/queryLeMengCard"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"
        context["cardUserNum"] = resp_json["data"]["cardUserNum"]

    @allure.story("查询乐檬存款记录")
    def test_member_deposit_get(self, client,context):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        resp = client.send("POST",
                           "/api/v1/wx-mini/member/queryLeMengDeposit",
                           json={
                                "pageNum": 1,
                                "pageSize": 10,
                                "sort": "DESC",
                                "cardUserNum": card_user_num
                            }
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    @allure.story("查询乐檬消费记录")
    def test_member_consume_get(self, client,context):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        resp = client.send("POST",
                           "/api/v1/wx-mini/member/queryLeMengConsume",
                           json={
                                "pageNum": 1,
                                "pageSize": 10,
                                "sort": "DESC",
                                "cardUserNum": card_user_num
                            }
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"


    @allure.story("获取微信支付组件token")
    def test_wx_pay_token(self, client):
        openid = client.user_data["openId"]
        resp = client.send("GET",
                           f"/api/v1/wx-mini/member/pay-view/{openid}"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    @allure.story("查看会员规则")
    def test_member_rule_get(self, client):
        resp = client.send("GET",
                           "/api/v1/wx-mini/member/rule"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    @allure.story("查询会员是否填写完标签")
    def test_member_check_tag(self, client):
        resp = client.send("GET",
                           "/api/v1/wx-mini/member/tag/checkFilled"
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"

    @allure.story("注销会员")
    @pytest.mark.skip(reason="拿不到verifyCode")
    def test_member_cancel(self, client):
        resp = client.send("POST",
                           "/api/v1/wx-mini/member/cancel",
                           json={
                                "memberId": 0,
                                "verifyCode": "string",
                                "isMemberCancel": True
                            }
                           )
        resp_json = resp.json()
        assert resp_json["msg"] == "成功"
