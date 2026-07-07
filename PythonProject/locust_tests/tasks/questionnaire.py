import random

from locust import SequentialTaskSet, TaskSet, task
from config import QUESTIONNAIRE_ID


class MemberBehavior(TaskSet):
    def on_start(self):
        self.member_info = self.user.member_info

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


__all__ = ['MemberBehavior']