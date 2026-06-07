from locust import SequentialTaskSet, task
from config import ACTIVITY_ID
from locust_tests.tasks import SharedData


class MemberBehavior(SequentialTaskSet):
    def on_start(self):
        with SharedData._member_lock:
            member_idx = SharedData.member_index
            SharedData.member_index = (SharedData.member_index + 1) % len(SharedData.member_pool)
        # print('================',SharedData.member_pool,member_idx)
        test_member = SharedData.member_pool[member_idx]
        member_rep = self.client.post("/api/v1/wx-mini/member/login/test", json={
            "phone": test_member.get("phone"),
            "areaCode": "86",
            "registerChannel": "WX_APPLET"
        })
        try:
            self.member_info = member_rep.json().get("data", {})
            self.client.headers.update({"auth-token": self.member_info.get("token", "")})
        except Exception as e:
            print(f"用户：{test_member.get('phone')}，响应结果： {member_rep.text}，错误：{e} ")
            self.interrupt(reschedule=False)

    def on_stop(self):
        print(f"用户 {self.member_info.get('phone')} 退出")


    @task
    def step1_get_activity_detail(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/activity/detail",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ACTIVITY_ID
            }
        )

    @task
    def step2_get_prize_details(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/activity/prize-details",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ACTIVITY_ID
            }
        )

    @task
    def step3_record_visit(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/activity/visit",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ACTIVITY_ID
            }
        )

    @task
    def step4_check_join_condition(self):
        check_rep = self.client.post(
            "/api/v1/wx-mini/marketing/activity/check",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ACTIVITY_ID
            }
        )
        check_data = check_rep.json().get("data", {})
        self.is_allowed = check_data.get("isAllowed", False)

    @task
    def step5_get_activity_times(self):
        times_rep = self.client.post(
            "/api/v1/wx-mini/marketing/activity/times",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ACTIVITY_ID
            }
        )
        times_data = times_rep.json().get("data", {})
        self.unused_times = times_data.get("unused", 0)

    @task
    def step6_join_activity(self):
        if self.is_allowed and self.unused_times > 0:
            self.client.post(
                "/api/v1/wx-mini/marketing/activity/join",
                json={
                    "memberId": self.member_info.get("memberId"),
                    "activityId": ACTIVITY_ID
                }
            )
        else:
            print(f"用户：{self.member_info.get('memberId')}，不满足参与条件: isAllowed={self.is_allowed}, unused={self.unused_times}")


__all__ = ['MemberBehavior']
