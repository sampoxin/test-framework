import random

from locust import SequentialTaskSet, TaskSet, task
from config import QUESTIONNAIRE_ID
from locust_tests.tasks import SharedData


class MemberBehavior(TaskSet):
    def on_start(self):
        """用户初始化：登录并保存用户信息"""
        # 从共享数据池获取用户信息
        with SharedData._member_lock:
            member_idx = SharedData.member_index
            SharedData.member_index = (SharedData.member_index + 1) % len(SharedData.member_pool)
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
                    "questionnaireId": QUESTIONNAIRE_ID,
                    "openid": self.parent.member_info.get("openId"), 
                    "unionid": self.parent.member_info.get("unionId"),
                    "memberId": self.parent.member_info.get("memberId")
                }
            ).json()
            assert detail_rep.get("success") == True, f"获取问卷详情失败，响应结果：{detail_rep}"
            self.detail_data = detail_rep.get("data")

        @task
        def step2_submit_questionnaire(self):
            """提交问卷"""
            questionnaire_list = self.detail_data.get("questionList", [])
            if not questionnaire_list:
                print("问卷列表为空，无法提交")
                return

            questionnaire_base = questionnaire_list[0]
            questionnaire_json = {
                "questionnaireId": QUESTIONNAIRE_ID,
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
            detail_rep = self.client.post(
                "/api/v1/wx-mini/marketing/questionnaire/submit",
                json=questionnaire_json
            ).json()
            assert detail_rep.get("success") == True, f"提交问卷失败，响应结果：{detail_rep}"
        
        @task
        def step3_exit(self):
            """退出嵌套任务集，返回父任务"""
            self.interrupt() 


    @task(1)
    def questionnaire_result(self):
        detail_rep = self.client.post(
            "/api/v1/wx-mini/marketing/questionnaire/review",
            json={
            "openid": self.member_info.get("openId"),
            "pageNum": 1,
            "pageSize": 10
        }).json()
        assert detail_rep.get("success") == True, f"获取问卷结果失败，响应结果：{detail_rep}"


# 导出 SharedData 供 locustfile.py 使用
__all__ = ['MemberBehavior', 'SharedData']