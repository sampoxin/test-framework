"""
Tasks 模块

导出可复用的 TaskSet 类，供 locustfile.py 引用
"""

from locust_tests.tasks.questionnaire import MemberBehavior as QuestionnaireBehavior
from locust_tests.tasks.activity import MemberBehavior as ActivityBehavior

__all__ = [
    'QuestionnaireBehavior',
    'ActivityBehavior'
]
