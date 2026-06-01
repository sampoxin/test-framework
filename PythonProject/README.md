## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
pytest -v

# 只运行冒烟测试
pytest -m p0 -v

# 运行核心测试
pytest -m "p0 or p1" -v

# 排除边界测试
pytest -m "not p3" -v
```

### 3. 切换测试环境

```bash
# 开发环境（默认）
pytest -v

# 测试环境
TEST_ENV=test pytest -v

# 生产环境（谨慎使用）
TEST_ENV=prod pytest -v
```

### 4. 生成报告

```bash
# 生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results

# 生成覆盖率报告
pytest --cov=api --cov=utils --cov-report=html
```

### 5. 性能测试

```bash
# 运行基准测试
pytest testcases/test_performance.py -v --benchmark

# 生成基准测试报告
pytest testcases/test_performance.py --benchmark-html=benchmark_report.html
```

---

## Locust 性能测试

### 1. 简介

Locust 是一个基于 Python 的开源性能测试工具，支持：
- 高并发模拟（基于 gevent 协程）
- 代码定义用户行为
- 实时 Web UI 监控
- 分布式测试

### 2. 目录结构

```
locust/
├── __init__.py          # 模块导出
└── demo.py              # 示例脚本
```

### 3. 运行 Locust

#### 3.1 Web UI 模式（推荐）

```bash
# 运行指定测试文件
locust -f locust/test_marketing.py

# 指定主机地址
locust -f locustfile.py --host=https://dev-ocss-gateway.youdtj.com
```

打开浏览器访问 http://localhost:8089 进行交互式测试。

#### 3.2 无头模式（CI/CD）

```bash
# 基本用法
locust -f locustfile.py --headless -u 100 -r 10 -t 5m

# 指定用户类
locust -f locustfile.py --headless -u 100 -r 10 -t 5m --users MemberUser

# 只显示摘要
locust -f locustfile.py --headless -u 50 -r 5 -t 2m --only-summary
```

#### 3.3 分布式测试

```bash
# Master 节点（控制节点）
locust -f locustfile.py --master --master-port=5557

# Worker 节点（执行节点）
locust -f locustfile.py --worker --master-host=127.0.0.1 --master-port=5557

# 等待所有 Worker 连接
locust -f locustfile.py --master --headless -u 1000 -r 50 --expect-workers=3
```

### 4. 常用参数说明

| 参数 | 说明 | 示例 |
| :--- | :--- | :--- |
| `-f` | 指定测试文件 | `-f locustfile.py` |
| `--headless` | 无界面模式 | `--headless` |
| `-u` | 虚拟用户数 | `-u 100` |
| `-r` | 每秒启动用户数 | `-r 10` |
| `-t` | 测试持续时间 | `-t 5m` |
| `--host` | 目标主机 | `--host=https://api.example.com` |
| `--users` | 指定用户类 | `--users MemberUser` |
| `--tags` | 只运行指定标签 | `--tags website` |
| `--exclude-tags` | 排除指定标签 | `--exclude-tags api` |
| `--only-summary` | 只显示摘要报告 | `--only-summary` |
| `--master` | 启动 Master 节点 | `--master` |
| `--worker` | 启动 Worker 节点 | `--worker` |
| `--master-host` | Master 节点地址 | `--master-host=192.168.1.100` |
| `--master-port` | Master 节点端口 | `--master-port=5557` |
| `--expect-workers` | 等待 Worker 数量 | `--expect-workers=3` |

### 5. 核心概念

#### 5.1 HttpUser（虚拟用户）

```python
from locust import HttpUser, task, between

class MyUser(HttpUser):
    host = "https://api.example.com"
    wait_time = between(1, 3)  # 任务间隔 1-3 秒
    
    @task(3)  # 权重为3
    def get_profile(self):
        self.client.get("/api/user/profile")
    
    @task(1)  # 权重为1
    def update_profile(self):
        self.client.post("/api/user/update", json={"name": "Test"})
```

#### 5.2 TaskSet（任务集合）

```python
from locust import TaskSet

class MemberBehavior(TaskSet):
    def on_start(self):
        """用户初始化（如登录）"""
        self.client.post("/api/login", json={"user": "test"})
    
    @task
    def browse(self):
        self.client.get("/api/products")
```

#### 5.3 SequentialTaskSet（顺序任务）

```python
from locust import SequentialTaskSet

class ShoppingFlow(SequentialTaskSet):
    @task
    def step1_browse(self):
        self.client.get("/api/products")
    
    @task
    def step2_add_cart(self):
        self.client.post("/api/cart/add")
```

### 6. 性能指标解读

| 指标 | 说明 | 参考值 |
| :--- | :--- | :--- |
| RPS | 每秒请求数 | 越高越好 |
| Avg | 平均响应时间 | < 200ms |
| Med | 中位数响应时间 | 接近 Avg |
| 95% | 95%请求响应时间 | < 500ms |
| 99% | 99%请求响应时间 | < 1s |
| Fail% | 失败率 | < 1% |

### 7. 测试策略

```bash
# 基准测试（稳定负载）
locust -f locustfile.py --headless -u 50 -r 5 -t 10m

# 负载测试（逐步加压）
locust -f locust/load_test.py --headless -t 5m

# 压力测试（极端负载）
locust -f locustfile.py --headless -u 500 -r 50 -t 2m

# 稳定性测试（长时间运行）
locust -f locustfile.py --headless -u 100 -r 2 -t 1h
```

---

## 测试用例编写规范

### 1. 数据驱动测试

在 `data/test_data.json` 中添加测试数据：

```json
{
  "member_update": [
    {
      "case_name": "更新名称-正常",
      "request_data": {"memberName": "TestUser"},
      "expected_code": "Success",
      "mark": "p0"
    }
  ]
}
```

### 2. 测试级别标记

| 标记 | 级别 | 描述 |
| :--- | :--- | :--- |
| `@pytest.mark.p0` | P0 | 冒烟测试，核心功能 |
| `@pytest.mark.p1` | P1 | 核心测试，主要流程 |
| `@pytest.mark.p2` | P2 | 功能测试，次要功能 |
| `@pytest.mark.p3` | P3 | 边界测试，边缘场景 |

### 3. Fixture 使用

```python
def test_member_info(self, client, context):
    """使用 client fixture 发送请求"""
    resp = client.send("GET", "/api/v1/wx-mini/member/profile")
    assert resp.json()["code"] == "Success"
```

## CI/CD 集成

```yaml
# .gitlab-ci.yml
stages:
  - smoke
  - regression
  - performance

smoke_test:
  stage: smoke
  script:
    - pytest -m p0 --tb=short
  only:
    - merge_requests

regression_test:
  stage: regression
  script:
    - pytest -m "p0 or p1" --cov=api --cov-report=html
  only:
    - develop

performance_test:
  stage: performance
  script:
    - pytest testcases/test_performance.py --benchmark
    - locust -f locust/load_test.py --headless -u 100 -r 10 -t 5m --only-summary
  only:
    - tags
```

## 配置说明

### test.yaml 配置项

| 配置项 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `env.default` | 默认环境 | dev |
| `servers.*.url` | 服务地址 | - |
| `servers.*.timeout` | 请求超时 | 30s |
| `parallel.workers` | 并行进程数 | 2 |
| `report.allure_dir` | Allure 报告目录 | reports/allure |

## 注意事项

1. 运行并行测试时，确保测试用例之间无共享状态
2. 生产环境测试需谨慎，建议使用独立的测试账号
3. 性能测试会产生大量请求，避免在生产环境频繁运行
4. Locust 测试建议使用独立的测试环境，避免影响线上服务

## 维护人员

- 测试开发团队

## 版本历史

- v1.0.0: 初始版本
- v1.1.0: 添加数据驱动测试
- v1.2.0: 支持并行测试
- v1.3.0: 添加性能测试支持
- v1.4.0: 集成 Locust 性能测试框架
