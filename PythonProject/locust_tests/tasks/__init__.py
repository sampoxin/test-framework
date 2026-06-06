"""
Tasks 模块

导出可复用的 TaskSet 类，供 locustfile.py 引用
"""

import threading

# 统一的共享数据类（所有任务模块共用）
class SharedData:
    member_index = 0
    member_pool = None
    _member_lock = threading.Lock()


from locust_tests.tasks.questionnaire import MemberBehavior as QuestionnaireBehavior
from locust_tests.tasks.activity import MemberBehavior as ActivityBehavior

__all__ = [
    'SharedData',
    'QuestionnaireBehavior',
    'ActivityBehavior'
]
