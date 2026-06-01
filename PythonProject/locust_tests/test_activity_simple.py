import threading
import csv

from locust import HttpUser, SequentialTaskSet, between, task, events
from config.settings import BASE_URL, TENANT


class MemberBehavior(SequentialTaskSet):
    def on_start(self):
        self.client.headers.update({"Content-Type": "application/json", "x-tenant": TENANT})

        with ActivityUser._member_lock:
            member_idx = ActivityUser.member_index
            ActivityUser.member_index = (ActivityUser.member_index + 1) % len(ActivityUser.member_pool)
        test_member = ActivityUser.member_pool[member_idx]
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
                "activityId": ActivityUser.activity_id
            }
        )

    @task
    def step2_get_prize_details(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/activity/prize-details",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ActivityUser.activity_id
            }
        )

    @task
    def step3_record_visit(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/activity/visit",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ActivityUser.activity_id
            }
        )

    @task
    def step4_check_join_condition(self):
        check_rep = self.client.post(
            "/api/v1/wx-mini/marketing/activity/check",
            json={
                "memberId": self.member_info.get("memberId"),
                "activityId": ActivityUser.activity_id
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
                "activityId": ActivityUser.activity_id
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
                    "activityId": ActivityUser.activity_id
                }
            )
        else:
            print(f"用户：{self.member_info.get('memberId')}，不满足参与条件: isAllowed={self.is_allowed}, unused={self.unused_times}")


class ActivityUser(HttpUser):
    host = BASE_URL
    wait_time = between(1, 2)
    tasks = [MemberBehavior]

    member_index = 0
    member_pool = None
    _member_lock = threading.Lock()

    activity_id = 450


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    try:
        with open("data/member_data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ActivityUser.member_pool = list(reader)
        print(f"✅ 用户池初始化成功，共 {len(ActivityUser.member_pool)} 个用户")
    except FileNotFoundError:
        print("❌ 用户数据文件不存在")
        raise
    except Exception as e:
        print(f"❌ 初始化用户池时出错: {e}")
        raise


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("✅ 所有用户测试完成")