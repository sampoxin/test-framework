"""
Locust 负载形状定义模块

提供多种负载加压策略，供不同测试场景使用
"""

from locust import LoadTestShape
import math


class StagedLoadShape(LoadTestShape):
    """
    阶梯式负载形状
    
    适用场景：模拟真实业务增长模式，逐步加压找到性能拐点
    """
    
    stages = [
        # 阶段1：预热期（0-30秒），10用户
        {"duration": 30, "users": 10, "spawn_rate": 2},
        
        # 阶段2：爬坡期（30-90秒），10→50用户
        {"duration": 90, "users": 50, "spawn_rate": 5},
        
        # 阶段3：稳定期（90-180秒），保持50用户
        {"duration": 180, "users": 50, "spawn_rate": 0},
        
        # 阶段4：加压期（180-270秒），50→100用户
        {"duration": 270, "users": 100, "spawn_rate": 8},
        
        # 阶段5：极限期（270-360秒），保持100用户
        {"duration": 360, "users": 100, "spawn_rate": 0},
        
        # 阶段6：下降期（360-420秒），100→0用户
        {"duration": 420, "users": 0, "spawn_rate": 5},
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        
        return None


class WaveLoadShape(LoadTestShape):
    """
    波浪式负载形状
    
    适用场景：模拟周期性波动的业务流量（如秒杀、活动促销）
    """
    
    min_users = 20
    max_users = 100
    wave_period = 60  # 波浪周期（秒）
    
    def tick(self):
        run_time = self.get_run_time()
        
        # 使用正弦函数生成波浪形负载
        wave = (math.sin(run_time / self.wave_period * 2 * math.pi) + 1) / 2
        users = int(self.min_users + wave * (self.max_users - self.min_users))
        
        # 限制最大运行时间为5分钟
        if run_time > 300:
            return None
        
        return users, 10


class ConcurrencyLoadShape(LoadTestShape):
    """
    并发突增负载形状
    
    适用场景：测试系统在突发流量下的稳定性
    """
    
    stages = [
        {"duration": 10, "users": 100, "spawn_rate": 50},   # 快速拉起
        {"duration": 60, "users": 100, "spawn_rate": 0},    # 保持高压
        {"duration": 70, "users": 200, "spawn_rate": 50},   # 再次突增
        {"duration": 120, "users": 200, "spawn_rate": 0},   # 保持更高压力
        {"duration": 130, "users": 300, "spawn_rate": 50},  # 极限压力
        {"duration": 180, "users": 300, "spawn_rate": 0},   # 极限保持
        {"duration": 190, "users": 0, "spawn_rate": 100},   # 快速释放
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        
        return None
