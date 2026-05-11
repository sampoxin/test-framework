import random
import allure
import pytest

from utils.tools import load_test_data

TEST_DATA = load_test_data("test_data.json")

@allure.epic("活动管理")
@allure.feature("问卷活动")
class TestMarketing:

    @allure.story("获取问卷详情")
    @pytest.mark.p0
    @pytest.mark.dependency(name="questionnaire_detail")
    def test_get_questionnaire_detail(self, client, context):
        user_data = client.user_data
        result = client.send("POST", "/api/v1/wx-mini/marketing/questionnaire/detail",
                             json={
                                "questionnaireId": 582,
                                "openid": user_data.get("openId"),
                                "unionid": user_data.get("unionId"),
                                "memberId": user_data.get("memberId")
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"
        question = result_json["data"]["questionList"][0]
        context["questionnaire_base"] = {
            "openid": user_data.get("openId"),
            "unionid": user_data.get("unionId"),
            "memberId": user_data.get("memberId"),
            "questionId": question["id"],
            "questionType": question["questionType"]
        }


    @allure.story("提交问卷")
    @pytest.mark.dependency(depends=["questionnaire_detail"])
    @pytest.mark.parametrize("data", TEST_DATA["questionnaire"], ids=[x["case_name"] for x in TEST_DATA["questionnaire"]])
    def test_submit_questionnaire(self, client, context, data):
        user_data = client.user_data
        questionnaire_base = context.get("questionnaire_base", {})
        questionnaire = {
            "questionnaireId": data["questionnaireId"],
            "openid": questionnaire_base.get("openid", user_data.get("openId")),
            "unionid": questionnaire_base.get("unionid", user_data.get("unionId")),
            "memberId": questionnaire_base.get("memberId", user_data.get("memberId")),
            "itemList": [
                {
                    "questionId": questionnaire_base.get("questionId", 1),
                    "questionType": questionnaire_base.get("questionType", 1),
                    "scoreValue": random.randint(1, 5),
                }
            ]
        }
        result = client.send("POST", "/api/v1/wx-mini/marketing/questionnaire/submit",
                             json=questionnaire)
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == data["expected_code"]

    @allure.story("获取该openid下所有问卷的点评")
    @pytest.mark.p0
    def test_get_questionnaire_result(self, client):
        result = client.send("POST", "/api/v1/wx-mini/marketing/questionnaire/review",
                             json={
                                "openid": client.user_data.get("openId"),
                                "pageNum": 1,
                                "pageSize": 10
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"
        assert result_json["data"]["total"] > 0