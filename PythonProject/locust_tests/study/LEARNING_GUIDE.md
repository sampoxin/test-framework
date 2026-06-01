# Locust 学习指南总结

## 课程文件列表

| 课程 | 文件 | 核心知识点 |
|------|------|-----------|
| 第一课 | [lesson1_basic.py](lesson1_basic.py) | HttpUser、@task、wait_time |
| 第二课 | [lesson2_taskset.py](lesson2_taskset.py) | TaskSet、on_start、on_stop |
| 第三课 | [lesson3_sequence.py](lesson3_sequence.py) | SequentialTaskSet、顺序执行 |
| 第四课 | [lesson5_parameters.py](lesson5_parameters.py) | HTTP方法、参数传递 |
| 第五课 | [lesson5_parameters.py](lesson5_parameters.py) | 数据驱动、参数化 |
| 第六课 | [lesson6_events.py](lesson6_events.py) | 事件监听、日志记录 |
| 第七课 | [lesson7_load_shape.py](lesson7_load_shape.py) | 自定义负载形状 |
| 第八课 | [lesson8_master_worker.py](lesson8_master_worker.py) | 分布式测试 |

## 核心概念速查表

### 1. 用户类（HttpUser）
```python
class MyUser(HttpUser):
    host = "https://api.example.com"  # 测试目标
    wait_time = between(1, 3)        # 任务间隔
    tasks = [MyTasks]                # 任务集合（可选）
```

### 2. 任务（@task）
```python
@task(3)  # 权重为3，概率 = 3/(所有权重之和)
def my_task(self):
    self.client.get("/api/endpoint")

@task
def another_task(self):  # 默认权重为1
    self.client.post("/api/data", json={"key": "value"})
```

### 3. 等待时间（wait_time）
```python
between(min, max)      # 随机等待
constant(n)           # 固定等待
constant_pacing(n)    # 固定间隔（自动调整）
```

### 4. 任务集合（TaskSet）
```python
class MyTasks(TaskSet):
    def on_start(self):      # 用户开始
        self.client.get("/login")
    
    @task
    def browse(self):
        self.client.get("/products")
    
    def on_stop(self):       # 用户结束
        self.client.get("/logout")
```

### 5. 常用命令
```bash
# 单机测试
locust -f locustfile.py                    # Web UI 模式
locust -f locustfile.py --headless -u 100 -r 10 -t 5m  # 无头模式

# 分布式测试
locust -f locustfile.py --master            # Master
locust -f locustfile.py --worker --master-host=127.0.0.1  # Worker
```

### 6. 关键指标
| 指标 | 说明 | 参考值 |
|------|------|--------|
| RPS | 每秒请求数 | 越高越好 |
| Avg | 平均响应时间 | < 200ms 优秀 |
| Med | 中位数响应时间 | 接近 Avg 较好 |
| 95% | 95%请求的响应时间 | < 500ms 优秀 |
| 99% | 99%请求的响应时间 | < 1s 优秀 |
| Fail% | 失败率 | < 1% 优秀 |

## 练习作业

### 初级练习
1. **修改 lesson1_basic.py**：添加一个新任务 `get_coupon_list`
2. **修改 lesson2_taskset.py**：在 `on_start` 中打印当前时间
3. **运行 lesson3_sequence.py**：观察任务执行顺序

### 中级练习
1. **编写数据驱动测试**：从文件读取测试用户数据
2. **添加事件监听**：统计所有请求的成功率
3. **实现混合场景**：70% 浏览，30% 提交

### 高级练习
1. **自定义负载形状**：模拟"预热 → 爬坡 → 稳定 → 下降"的完整周期
2. **分布式测试**：用两台机器测试 1000 并发用户
3. **性能对比**：对比单接口和混合场景的性能差异

## 学习路径建议

1. **第一天**：完成 lesson1-3，理解基本概念
2. **第二天**：完成 lesson4-5，掌握数据驱动
3. **第三天**：完成 lesson6-7，学会高级功能
4. **第四天**：完成 lesson8，了解分布式架构
5. **第五天**：综合练习，编写完整的性能测试脚本

## 常见错误排查

### 错误1：AttributeError: 'NoneType' object has no attribute 'get'
```python
# 问题：response.json() 返回 None
data = response.json()
data.get("xxx")  # 报错

# 解决：添加异常处理
try:
    data = response.json()
    if data:
        value = data.get("xxx")
except Exception:
    pass
```

### 错误2：用户不执行任务
```python
# 问题：只定义了 tasks 属性但没有创建 TaskSet

# 解决1：直接定义 @task
class User(HttpUser):
    @task
    def my_task(self):
        pass

# 解决2：创建 TaskSet
class MyTasks(TaskSet):
    @task
    def my_task(self):
        pass

class User(HttpUser):
    tasks = [MyTasks]
```

### 错误3：wait_time 不生效
```python
# 问题：在 TaskSet 中设置了 wait_time

# 解决：wait_time 应该设置在 HttpUser 上，不是 TaskSet
class User(HttpUser):
    wait_time = between(1, 3)  # ✓ 正确
    tasks = [MyTasks]

class MyTasks(TaskSet):
    # wait_time = between(1, 3)  # ✗ 无效
    pass
```

## 下一步学习

1. **深入理解 gevent**：了解协程和事件循环的原理
2. **学习性能分析**：如何识别性能瓶颈
3. **集成 CI/CD**：将 Locust 集成到 Jenkins/GitLab CI
4. **监控告警**：设置性能阈值告警
5. **报告自动化**：生成 HTML 报告并自动发送邮件

---

祝你学习愉快！有问题随时问我。
