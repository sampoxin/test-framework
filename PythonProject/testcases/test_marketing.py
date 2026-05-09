import random
import allure


@allure.epic("活动管理")
@allure.feature("问卷活动")
class TestMarketing:

    @allure.story("获取问卷详情")
    def test_get_questionnaire_detail(self, client,context):
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
        assert result_json["msg"] == "成功"
        question = result_json["data"]["questionList"][0]
        context["questionnaire"] = {
            "questionnaireId": 582,
            "openid": user_data.get("openId"),
            "unionid": user_data.get("unionId"),
            "memberId": user_data.get("memberId"),
            "itemList": [
                {
                    "questionId": question["id"],
                    "questionType": question["questionType"],
                    "scoreValue": random.randint(1, 5),
                }
            ]
        }

    @allure.story("提交问卷")
    def test_submit_questionnaire(self, client,context):
        result = client.send("POST", "/api/v1/wx-mini/marketing/questionnaire/submit",
                             json=context.get("questionnaire"))
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["msg"] == "成功"

    @allure.story("获取该openid下所有问卷的点评")
    def test_get_questionnaire_result(self, client):
        result = client.send("POST", "/api/v1/wx-mini/marketing/questionnaire/review",
                             json={
                                "openid": client.user_data.get("openId"),
                                "pageNum": 1,
                                "pageSize": 10
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["msg"] == "成功"
        assert result_json["data"]["total"] > 0