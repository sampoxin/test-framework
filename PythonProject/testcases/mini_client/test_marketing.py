import random

import allure
import pytest

from config import QUESTIONNAIRE_ID
from utils.tools import load_test_data

TEST_DATA = load_test_data("test_data.json")


@allure.epic("活动管理")
@allure.feature("问卷活动")
class TestMarketing:

    @allure.story("获取问卷详情")
    @pytest.mark.p0
    @pytest.mark.dependency(name="questionnaire_detail")
    def test_get_questionnaire_detail(self, marketing_api, client, context):
        user_data = client.user_data
        result = marketing_api.get_detail(
            QUESTIONNAIRE_ID,
            user_data.get("openId"),
            user_data.get("unionId"),
            user_data.get("memberId")
        )
        question = result["data"]["questionList"][0]
        context["questionnaire_base"] = {
            "openid": user_data.get("openId"),
            "unionid": user_data.get("unionId"),
            "memberId": user_data.get("memberId"),
            "questionId": question["id"],
            "questionType": question["questionType"]
        }

    @allure.story("提交问卷")
    @pytest.mark.dependency(depends=["questionnaire_detail"])
    @pytest.mark.parametrize("data", TEST_DATA["questionnaire"],
                             ids=[x["case_name"] for x in TEST_DATA["questionnaire"]])
    def test_submit_questionnaire(self, marketing_api, client, context, data):
        user_data = client.user_data
        questionnaire_base = context.get("questionnaire_base", {})

        # 正常提交问卷使用配置的ID，其他测试用例使用data中的值
        q_id = QUESTIONNAIRE_ID if data["case_name"] == "提交问卷-Success" else data["questionnaireId"]

        item_list = [{
            "questionId": questionnaire_base.get("questionId", 1),
            "questionType": questionnaire_base.get("questionType", 1),
            "scoreValue": random.randint(1, 5),
        }]

        result = marketing_api.submit(
            q_id,
            questionnaire_base.get("openid", user_data.get("openId")),
            questionnaire_base.get("unionid", user_data.get("unionId")),
            questionnaire_base.get("memberId", user_data.get("memberId")),
            item_list
        )
        assert result["code"] == data["expected_code"]

    @allure.story("获取该openid下所有问卷的点评")
    @pytest.mark.p0
    def test_get_questionnaire_result(self, marketing_api, client):
        result = marketing_api.get_review(client.user_data.get("openId"))
        assert result["data"]["total"] > 0
