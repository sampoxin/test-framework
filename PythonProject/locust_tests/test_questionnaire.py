import threading

from locust import HttpUser, SequentialTaskSet, between,TaskSet,task,events
from config.settings import BASE_URL, TENANT
import random
import pandas as pd



class MemberBehavior(TaskSet):
    def on_start(self):
        """用户初始化：登录并保存用户信息"""
        self.client.headers.update({"Content-Type": "application/json", "x-tenant": TENANT})

        # 2.按顺序从用户池中获取用户信息
        with QuestionnaireUser._member_lock:
            member_idx = QuestionnaireUser.member_index
            QuestionnaireUser.member_index = (QuestionnaireUser.member_index + 1) % len(QuestionnaireUser.member_pool)
        test_member = QuestionnaireUser.member_pool[member_idx]
        member_rep = self.client.post( "/api/v1/wx-mini/member/login/test", json={
            "phone": test_member.get("phone"),
            "areaCode": "86",
            "registerChannel": "WX_APPLET"
        })
        self.member_info = member_rep.json().get("data", {})
        self.client.headers.update({"auth-token": self.member_info.get("token", "")})

    def on_stop(self):
        """用户退出：清除登录状态"""
        print(f"用户 {self.member_info.get('phone')} 退出")
    
    @task(3)
    class TakeQuestionnaire(SequentialTaskSet):
        """参与问卷"""
        @task
        def step1_questionnaire_detail(self):
            """获取问卷详情"""
            detail_rep = self.client.post(
                "/api/v1/wx-mini/marketing/questionnaire/detail",
                json={
                    "questionnaireId": 582,
                    "openid": self.parent.member_info.get("openId"), 
                    "unionid": self.parent.member_info.get("unionId"),
                    "memberId": self.parent.member_info.get("memberId")
                }
            )
            self.detail_data = detail_rep.json().get("data")

        @task
        def step2_submit_questionnaire(self):
            """提交问卷"""
            questionnaire_list = self.detail_data.get("questionList", [])
            if not questionnaire_list:
                self.logger.info("问卷列表为空，无法提交")
                return

            questionnaire_base = questionnaire_list[0]
            questionnaire_json = {
                "questionnaireId": 582,
                "openid": self.parent.member_info.get("openId"), 
                "unionid": self.parent.member_info.get("unionId"),
                "memberId": self.parent.member_info.get("memberId"),
                "itemList": [
                    {
                        "questionId": questionnaire_base.get("id", 1),
                        "questionType": questionnaire_base.get("questionType", 1),
                        "scoreValue": random.randint(1, 5),
                    }
                ]
            }
            self.client.post(
                "/api/v1/wx-mini/marketing/questionnaire/submit",
                json=questionnaire_json
            )
        
        @task
        def step3_exit(self):
            """退出嵌套任务集，返回父任务"""
            self.interrupt() 


    @task(1)
    def questionnaire_result(self):
        self.client.post(
            "/api/v1/wx-mini/marketing/questionnaire/review",
            json={
            "openid": self.member_info.get("openId"),
            "pageNum": 1,
            "pageSize": 10
        })

class QuestionnaireUser(HttpUser):
    host = BASE_URL
    wait_time = between(1, 2)
    tasks = [MemberBehavior]

    # 类属性：保存用户信息
    member_index = 0
    member_pool = None
    _member_lock = threading.Lock()  # 添加线程锁


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时执行一次，初始化用户池"""
    try:
        df = pd.read_csv("data/member_data.csv", encoding="utf-8")
        QuestionnaireUser.member_pool = df.to_dict(orient="records")
        print(f"✅ 用户池初始化成功，共 {len(QuestionnaireUser.member_pool)} 个用户")
    except FileNotFoundError:
        print("❌ 用户数据文件不存在")
        raise
    except Exception as e:
        print(f"❌ 初始化用户池时出错: {e}")
        raise

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时执行一次"""
    print("✅ 所有用户测试完成")


# ========================================
# 添加请求监听器（全局监听所有请求）
# ========================================
# @events.request.add_listener
# def log_request_details(request_type, name, response_time, response_length, exception, context, **kwargs):
#     """
#     监听所有请求，记录详细信息
#     """
#     if exception:
#         print(f"\n❌ 请求失败")
#         print(f"   类型: {request_type}")
#         print(f"   URL: {name}")
#         print(f"   错误: {str(exception)}")
#     else:
#         print(f"✅ 请求成功")
#         print(f"   类型: {request_type}")
#         print(f"   URL: {name}")
#         print(f"   耗时: {response_time:.2f}ms")
#         print(f"   响应大小: {response_length} bytes")