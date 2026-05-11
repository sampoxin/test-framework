# 基准测试（接口响应时间）
import allure


@allure.epic("性能测试")
@allure.feature("接口基准测试")
class TestMemberPerformance:
    """会员模块性能测试"""

    @allure.story("获取会员信息")
    def test_member_info_benchmark(self, client, benchmark):
        benchmark(client.send, "GET", "/api/v1/wx-mini/member/profile")

    @allure.story("更新会员信息")
    def test_member_update_benchmark(self, client, benchmark):
        benchmark(
            client.send,
            "POST",
            "/api/v1/wx-mini/member/update",
            json={"memberId": client.user_data["memberId"], "memberName": "Test"}
        )


class TestMarketingPerformance:
    """营销模块性能测试"""

    @allure.story("提交问卷")
    def test_questionnaire_submit_benchmark(self, client, benchmark):
        benchmark(
            client.send,
            "POST",
            "/api/v1/wx-mini/marketing/questionnaire/submit",
            json={
                "questionnaireId": 582,
                "memberId": client.user_data["memberId"],
                "itemList": [{"questionId": 1, "scoreValue": 3}]
            }
        )