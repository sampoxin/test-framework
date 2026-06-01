"""
Locust 课程第七课：自定义负载形状
==================================
目标：学会使用 LoadTestShape 实现复杂的负载变化模式

运行命令：
    locust -f lesson7_load_shape.py --headless -t 60s
    注意：不需要指定 -u 参数，用户数由 LoadTestShape 控制
"""

from locust import HttpUser, task, between, LoadTestShape
import random


class LoadTestUser(HttpUser):
    """
    普通用户类，不指定具体的用户数
    用户数由 StagedLoadShape 动态控制
    """
    host = "https://dev-ocss-gateway.youdtj.com"
    wait_time = between(1, 2)
    
    @task(2)
    def browse(self):
        self.client.get("/api/v1/wx-mini/member/profile")
    
    @task(1)
    def submit(self):
        self.client.post(
            "/api/v1/wx-mini/member/update",
            json={"memberId": "123456", "memberName": f"User_{random.randint(1, 999)}"}
        )


class StagedLoadShape(LoadTestShape):
    """
    LoadTestShape：自定义负载形状
    
    作用：定义用户数随时间变化的模式
    
    常见的负载测试阶段：
    1. 预热期：少量用户，检查系统是否正常工作
    2. 爬坡期：逐步增加用户，找到性能拐点
    3. 高压期：持续高负载，观察系统稳定性
    4. 下降期：逐步减少用户，观察系统恢复能力
    """
    
    stages = [
        # 阶段1：预热（0-20秒），10个用户
        {"duration": 20, "users": 10, "spawn_rate": 2},
        
        # 阶段2：爬坡（20-60秒），10→50用户
        {"duration": 60, "users": 50, "spawn_rate": 5},
        
        # 阶段3：高负载（60-120秒），保持50用户
        {"duration": 120, "users": 50, "spawn_rate": 0},
        
        # 阶段4：加压（120-180秒），50→100用户
        {"duration": 180, "users": 100, "spawn_rate": 10},
        
        # 阶段5：极限（180-240秒），保持100用户
        {"duration": 240, "users": 100, "spawn_rate": 0},
        
        # 阶段6：下降（240-300秒），100→0用户
        {"duration": 300, "users": 0, "spawn_rate": 20},
    ]
    
    def tick(self):
        """
        tick() 方法会被定期调用，返回 (用户数, 生成速率)
        
        返回值：
        - None: 测试结束
        - (users, spawn_rate): 调整到指定用户数
        """
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        
        return None  # 所有阶段执行完毕


"""
思考题：
1. spawn_rate 设为 0 是什么意思？用户数会怎样变化？
2. 如何判断系统的性能拐点？
3. 什么情况下需要设置下降期？
"""