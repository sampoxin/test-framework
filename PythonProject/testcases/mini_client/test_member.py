import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields

TEST_DATA = load_test_data("test_mini_api_data.json")


@allure.epic("会员管理")
@allure.feature("会员信息")
class TestMember:

    @allure.story("获取会员信息")
    @pytest.mark.p0
    def test_member_info_get(self, member_api, client, context):
        result = member_api.get_profile()
        assert result["data"]["phone"] == client.user_data["phone"]
        context["memberType"] = result["data"]["typeId"]

    @allure.story("检查会员是否可以更新生日")
    @pytest.mark.p0
    def test_check_birthday_get(self, member_api, context):
        result = member_api.check_update_birthday()
        context["isCheckBrith"] = result["data"]

    @allure.story("查询会员标签")
    @pytest.mark.p0
    def test_member_tag_get(self, member_api, context):
        member_type = context.get("memberType")
        if member_type is None:
            pytest.skip("前置用例未生成 member_type")
        member_api.get_tag_info(member_type)

    @allure.story("更新会员信息")
    @pytest.mark.parametrize("data", TEST_DATA["member_update"],
                             ids=[x["case_name"] for x in TEST_DATA["member_update"]])
    def test_member_update(self, member_api, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        result = member_api.update(client.user_data["memberId"], **data_fields)
        assert result["code"] == data["expected_code"]

    @allure.story("更新会员生日")
    @pytest.mark.parametrize("data", TEST_DATA["member_birthday"],
                             ids=[x["case_name"] for x in TEST_DATA["member_birthday"]])
    def test_member_birthday_put(self, member_api, client, context, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        result = member_api.update(client.user_data["memberId"], **data_fields)
        is_check = context.get("isCheckBrith")
        assert result["code"] == "Success" if is_check else "MEMBER_MODIFY_BIRTHDAY_YEAR_LIMIT"

    @allure.story("更新会员头像")
    @pytest.mark.parametrize("data", TEST_DATA["member_avatar"],
                             ids=[x["case_name"] for x in TEST_DATA["member_avatar"]])
    def test_member_avatar_put(self, member_api, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        result = member_api.update(client.user_data["memberId"], **data_fields)
        assert result["code"] == data["expected_code"]

    @allure.story("查询乐檬会员卡余额")
    @pytest.mark.p0
    def test_member_lmcard_get(self, member_api, context):
        result = member_api.get_le_meng_card()
        context["cardUserNum"] = result["data"]["cardUserNum"]

    @allure.story("查询乐檬存款记录")
    @pytest.mark.parametrize("data", TEST_DATA["member_lm_deposit"],
                             ids=[x["case_name"] for x in TEST_DATA["member_lm_deposit"]])
    def test_member_deposit_get(self, member_api, context, data):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        data_fields = data["request_data"]
        if "cardUserNum" not in data_fields:
            data_fields["cardUserNum"] = card_user_num
        result = member_api.get_le_meng_deposit(**data_fields)
        assert result["code"] == data["expected_code"]

    @allure.story("查询乐檬消费记录")
    @pytest.mark.parametrize("data", TEST_DATA["member_lm_consume"],
                             ids=[x["case_name"] for x in TEST_DATA["member_lm_consume"]])
    def test_member_consume_get(self, member_api, context, data):
        card_user_num = context.get("cardUserNum")
        if card_user_num is None:
            pytest.skip("前置用例未生成 card_user_num")
        data_fields = data["request_data"]
        if "cardUserNum" not in data_fields:
            data_fields["cardUserNum"] = card_user_num
        result = member_api.get_le_meng_consume(**data_fields)
        assert result["code"] == data["expected_code"]

    @allure.story("获取微信支付组件token")
    @pytest.mark.p0
    def test_wx_pay_token(self, member_api, client):
        member_api.get_pay_token(client.user_data["openId"])

    @allure.story("查看会员规则")
    @pytest.mark.p0
    def test_member_rule_get(self, member_api):
        member_api.get_rule()

    @allure.story("查询会员是否填写完标签")
    @pytest.mark.p0
    def test_member_check_tag(self, member_api):
        member_api.check_tag_filled()

    @allure.story("注销会员")
    @pytest.mark.skip(reason="拿不到verifyCode")
    def test_member_cancel(self, member_api):
        member_api.cancel(member_id=0, verify_code="string")
