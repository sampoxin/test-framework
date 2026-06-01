"""
Locust 课程第八课：分布式测试
==============================
目标：理解 Locust 的分布式架构，学会启动 Master 和 Worker

适用场景：
- 单机无法模拟足够多的并发（通常单机支持 1000-3000 用户）
- 需要多台机器协同模拟更大规模的负载

架构说明：
┌─────────────────┐
│   Master 节点    │  控制节点，运行 Web UI，收集数据
└────────┬────────┘
         │  TCP (5557)
         ▼
┌─────────────────┐
│   Worker 节点1   │  执行节点，运行虚拟用户
└────────┬────────┘
         │  TCP (5557)
         ▼
┌─────────────────┐
│   Worker 节点2   │  执行节点，运行虚拟用户
└─────────────────┘

启动命令：

# 终端1：启动 Master（控制节点）
locust -f locustfile.py --master

# 终端2：启动 Worker 1
locust -f locustfile.py --worker --master-host=127.0.0.1

# 终端3：启动 Worker 2
locust -f locustfile.py --worker --master-host=127.0.0.1

# 也可以使用不同端口
locust -f locustfile.py --master --master-port=5557
locust -f locustfile.py --worker --master-host=127.0.0.1 --master-port=5557

# 无头模式（无 Web UI，通过命令行控制）
locust -f locustfile.py \
    --master \
    --headless \
    -u 1000 \
    -r 100 \
    -t 5m \
    --expect-workers=2
"""

from locust import HttpUser, task, between


class DistributedUser(HttpUser):
    """
    分布式测试的用户类
    与单机测试完全相同，不需要任何修改
    """
    host = "https://dev-ocss-gateway.youdtj.com"
    wait_time = between(1, 2)
    
    @task(3)
    def get_profile(self):
        self.client.get("/api/v1/wx-mini/member/profile")
    
    @task(2)
    def get_points(self):
        self.client.get("/api/v1/wx-mini/member/points?memberId=123456")
    
    @task(1)
    def update_profile(self):
        self.client.post(
            "/api/v1/wx-mini/member/update",
            json={"memberId": "123456", "memberName": "LoadTest"}
        )


"""
常见问题：

Q: 需要多少台 Worker？
A: 取决于单机能支持多少用户。通常：
   - 简单请求（GET）：单机能支持 2000-3000 用户
   - 复杂请求（POST + JSON）：单机能支持 1000-1500 用户
   - 需要 TLS/SSL：单机能支持 500-1000 用户

Q: Master 挂了怎么办？
A: Worker 会继续运行，但无法再控制。可以使用 --expect-workers 参数，
   确保所有 Worker 都连接后再开始测试。

Q: 如何估算需要的并发数？
A: 
   1. 先进行小规模测试，记录单个用户的 RPS
   2. 目标 RPS / 单用户 RPS = 需要的用户数
   3. 考虑 20-30% 的余量
   
   例如：
   - 单用户测试得到 5 RPS
   - 目标 1000 RPS
   - 需要 1000 / 5 = 200 用户
   - 考虑余量：200 * 1.3 ≈ 260 用户

Q: Worker 之间需要网络互通吗？
A: 是的，所有 Worker 需要能连接到 Master 的 5557 端口。
   Worker 之间不需要通信。
"""

# ========================================
# 多主机测试（高级）
# ========================================

"""
如果你需要测试多个目标服务器，可以使用 tag 功能：

class WebUser(HttpUser):
    @task(tags=["website"])
    def visit_website(self):
        self.client.get("https://website.example.com")

class APIUser(HttpUser):
    @task(tags=["api"])
    def call_api(self):
        self.client.get("https://api.example.com")

运行命令：
# 只测试 website
locust -f locustfile.py --tags website

# 排除 api
locust -f locustfile.py --exclude-tags api
"""
