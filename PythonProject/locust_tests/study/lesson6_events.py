"""
Locust 课程第六课：事件监听和自定义日志
=========================================
目标：理解 Locust 的事件系统，学会添加自定义监控

运行命令：
    locust -f lesson6_events.py --headless -u 3 -r 1 -t 10s
"""

from locust import HttpUser, task, between, events
import random


class EventDemoUser(HttpUser):
    host = "https://dev-ocss-gateway.youdtj.com"
    wait_time = between(1, 2)
    
    @task(2)
    def success_request(self):
        """这个请求大概率会成功"""
        self.client.get("/api/v1/wx-mini/member/profile")
    
    @task(1)
    def random_fail_request(self):
        """模拟随机失败的请求"""
        if random.random() < 0.3:  # 30% 概率失败
            self.client.get("/api/v1/nonexistent/endpoint")
        else:
            self.client.get("/api/v1/wx-mini/member/profile")


# ========================================
# 事件监听器
# ========================================

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """
    每次请求完成时触发（无论成功还是失败）
    
    参数说明：
    - request_type: HTTP 方法，如 GET、POST
    - name: 请求的 URL 或命名的名称
    - response_time: 响应时间（毫秒）
    - response_length: 响应体大小（字节）
    - exception: 异常对象，如果有的话
    """
    if exception:
        # 请求失败
        print(f"❌ 请求失败 | {request_type} {name} | 耗时: {response_time}ms | 错误: {exception}")
    else:
        # 请求成功
        print(f"✅ 请求成功 | {request_type} {name} | 耗时: {response_time}ms | 大小: {response_length}bytes")


@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, exception, **kwargs):
    """
    请求失败时触发（仅在失败时）
    这个事件在 request 事件之后触发
    """
    print(f"🔴 处理失败请求 | {request_type} {name} | 耗时: {response_time}ms")


@events.request_success.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """
    请求成功时触发（仅在成功时）
    这个事件在 request 事件之后触发
    """
    print(f"🟢 处理成功请求 | {request_type} {name} | 耗时: {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    测试开始时触发（所有用户生成完毕后）
    """
    print("=" * 50)
    print("🚀 测试开始！")
    print(f"   目标主机: {environment.host}")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    测试结束时触发
    """
    stats = environment.stats
    
    print("=" * 50)
    print("🏁 测试结束！")
    print("   统计摘要：")
    print(f"   - 总请求数: {stats.total.request_count}")
    print(f"   - 失败请求: {stats.total.failure_count}")
    print(f"   - 平均响应: {stats.total.avg_response_time:.2f}ms")
    print(f"   - 中位响应: {stats.total.median_response_time:.2f}ms")
    print(f"   - 95分位:   {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"   - 99分位:   {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print("=" * 50)


@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    """
    所有虚拟用户创建完成时触发
    """
    print(f"👥 所有 {user_count} 个虚拟用户已就绪！")


"""
思考题：
1. request 和 request_success/request_failure 有什么区别？哪个先触发？
2. 如何在事件监听器中统计特定接口的成功率？
3. 如何在测试结束后自动发送邮件通知？
"""