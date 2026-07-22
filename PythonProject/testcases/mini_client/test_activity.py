import allure
import pytest

from config import ACTIVITY_ID


@allure.epic("活动管理")
@allure.feature("营销活动")
class TestActivity:

    @allure.story("获取活动详情")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_detail")
    def test_get_activity_detail(self, activity_api, client, context):
        member_id = client.user_data.get("memberId")
        result = activity_api.get_detail(member_id, ACTIVITY_ID)
        context["activity_data"] = {
            "memberId": member_id,
            "activityId": ACTIVITY_ID
        }

    @allure.story("获取活动奖品详情")
    @pytest.mark.p0
    def test_get_activity_prize_details(self, activity_api, client, context):
        activity_data = context.get("activity_data", {})
        activity_api.get_prize_details(
            activity_data.get("memberId", client.user_data.get("memberId")),
            activity_data.get("activityId", ACTIVITY_ID)
        )

    @allure.story("记录活动访问")
    @pytest.mark.p0
    def test_record_activity_visit(self, activity_api, client, context):
        activity_data = context.get("activity_data", {})
        activity_api.record_visit(
            activity_data.get("memberId", client.user_data.get("memberId")),
            activity_data.get("activityId", ACTIVITY_ID)
        )

    @allure.story("查询活动次数")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_times")
    def test_get_activity_times(self, activity_api, client, context):
        activity_data = context.get("activity_data", {})
        result = activity_api.get_times(
            activity_data.get("memberId", client.user_data.get("memberId")),
            activity_data.get("activityId", ACTIVITY_ID)
        )
        context["unused_times"] = result["data"].get("unused", 0)

    @allure.story("检查活动参与条件")
    @pytest.mark.p0
    @pytest.mark.dependency(name="activity_check")
    def test_check_activity_condition(self, activity_api, client, context):
        activity_data = context.get("activity_data", {})
        result = activity_api.check_condition(
            activity_data.get("memberId", client.user_data.get("memberId")),
            activity_data.get("activityId", ACTIVITY_ID)
        )
        context["is_allowed"] = result["data"].get("isAllowed", False)

    @allure.story("参与活动")
    @pytest.mark.p0
    @pytest.mark.dependency(depends=["activity_detail", "activity_times", "activity_check"])
    def test_join_activity(self, activity_api, context):
        activity_data = context.get("activity_data", {})
        unused_times = context.get("unused_times", 0)
        is_allowed = context.get("is_allowed", False)

        if is_allowed and unused_times > 0:
            activity_api.join(
                activity_data.get("memberId"),
                activity_data.get("activityId")
            )
        else:
            pytest.skip(f"不满足参与条件: isAllowed={is_allowed}, unused={unused_times}")
