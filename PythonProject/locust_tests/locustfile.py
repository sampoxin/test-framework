"""
Locust 性能测试主入口文件

使用方法：
    # 普通模式（指定用户数）
    $env:LOCUST_ENV="dev"
    locust -f locust_tests/locustfile.py --headless -u 10 -t 60s --html=reports/locust-report/report.html
    
    # 负载形状模式（由 LoadTestShape 控制用户数）
    $env:LOCUST_ENV="dev"
    locust -f locust_tests/locustfile.py --headless -t 420s --html=reports/locust-report/report.html

支持的任务：
    - 问卷测试 (tasks/questionnaire.py)
    - 活动测试 (tasks/activity.py)
    
支持的负载形状：
    - StagedLoadShape: 阶梯式负载（默认）
    - WaveLoadShape: 波浪式负载
    - ConcurrencyLoadShape: 并发突增负载
"""

import csv
import os
from locust import HttpUser, between, events
from locust_tests.tasks import QuestionnaireBehavior, ActivityBehavior
from config import config, BASE_URL, TENANT, CURRENT_ENV

# 根据环境变量选择负载形状
SHAPE_TYPE = os.getenv("LOAD_SHAPE", "staged")
if SHAPE_TYPE == "staged":
    from locust_tests.core.load_shapes import StagedLoadShape
elif SHAPE_TYPE == "wave":
    from locust_tests.core.load_shapes import WaveLoadShape
elif SHAPE_TYPE == "concurrency":
    from locust_tests.core.load_shapes import ConcurrencyLoadShape

# 获取当前配置
current_config = config._current_config

# 打印当前配置信息
print(f"\n>>> 测试环境: {CURRENT_ENV}")
print(f">>> API地址: {BASE_URL}\n")


class TestUser(HttpUser):
    """统一测试用户类"""
    host = BASE_URL
    wait_time = between(1, 2)

    def on_start(self):
        """用户初始化"""
        self.client.headers.update({
            "Content-Type": "application/json",
            "x-tenant": TENANT
        })
    
    # 引用任务集（权重3:1）
    tasks = {
        # QuestionnaireBehavior: 3,
        ActivityBehavior: 1
    }


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时执行一次，初始化用户池"""
    from locust_tests.tasks import SharedData
    
    try:
        # 使用配置的数据文件
        data_file = current_config.get('data_file', 'data/dev_member_data.csv')
        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            SharedData.member_pool = list(reader)
        print(f"用户池初始化成功，共 {len(SharedData.member_pool)} 个用户")
        print(f"数据文件: {data_file}")
    except FileNotFoundError:
        print(f"用户数据文件不存在: {data_file}")
        environment.runner.quit()
    except Exception as e:
        print(f"初始化用户池时出错: {e}")
        environment.runner.quit()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时执行一次"""
    print("所有用户测试完成")
