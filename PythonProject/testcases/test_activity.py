import allure
import pytest


activityId = 450

@allure.epic("活动管理")
@allure.feature("营销活动")
class TestActivity:

    @allure.story("获取活动详情")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_detail")
    def test_get_activity_detail(self, client, context):
        user_data = client.user_data
        result = client.send("POST", "/api/v1/wx-mini/marketing/activity/detail",
                            json={
                                "memberId": user_data.get("memberId"),
                                "activityId": activityId
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"
        context["activity_data"] = {
            "memberId": user_data.get("memberId"),
            "activityId": activityId
        }

    @allure.story("获取活动奖品详情")
    @pytest.mark.p0
    def test_get_activity_prize_details(self, client, context):
        activity_data = context.get("activity_data", {})
        result = client.send("POST", "/api/v1/wx-mini/marketing/activity/prize-details",
                            json={
                                "memberId": activity_data.get("memberId", client.user_data.get("memberId")),
                                "activityId": activity_data.get("activityId", activityId)
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"

    @allure.story("记录活动访问")
    @pytest.mark.p0
    def test_record_activity_visit(self, client, context):
        activity_data = context.get("activity_data", {})
        result = client.send("POST", "/api/v1/wx-mini/marketing/activity/visit",
                            json={
                                "memberId": activity_data.get("memberId", client.user_data.get("memberId")),
                                "activityId": activity_data.get("activityId", activityId)
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"

    @allure.story("查询活动次数")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_times")
    def test_get_activity_times(self, client, context):
        activity_data = context.get("activity_data", {})
        result = client.send("POST", "/api/v1/wx-mini/marketing/activity/times",
                            json={
                                "memberId": activity_data.get("memberId", client.user_data.get("memberId")),
                                "activityId": activity_data.get("activityId", activityId)
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"
        context["unused_times"] = result_json["data"].get("unused", 0)

    @allure.story("检查活动参与条件")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_check")
    def test_check_activity_condition(self, client, context):
        activity_data = context.get("activity_data", {})
        result = client.send("POST", "/api/v1/wx-mini/marketing/activity/check",
                            json={
                                "memberId": activity_data.get("memberId", client.user_data.get("memberId")),
                                "activityId": activity_data.get("activityId", activityId)
                            })
        result_json = result.json()
        assert result.status_code == 200
        assert result_json["code"] == "Success"
        context["is_allowed"] = result_json["data"].get("isAllowed", False)

    @allure.story("参与活动")
    @pytest.mark.p0
    @pytest.mark.dependency(depends=["activity_detail", "activity_times", "activity_check"])
    def test_join_activity(self, client, context):
        activity_data = context.get("activity_data", {})
        unused_times = context.get("unused_times", 0)
        is_allowed = context.get("is_allowed", False)

        if is_allowed and unused_times > 0:
            result = client.send("POST", "/api/v1/wx-mini/marketing/activity/join",
                                json={
                                    "memberId": activity_data.get("memberId", client.user_data.get("memberId")),
                                    "activityId": activity_data.get("activityId", activityId)
                                })
            result_json = result.json()
            assert result.status_code == 200
            assert result_json["code"] == "Success"
        else:
            pytest.skip(f"不满足参与条件: isAllowed={is_allowed}, unused={unused_times}")