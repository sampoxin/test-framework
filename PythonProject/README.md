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
pytest --alluredir=reports/allure
allure serve reports/allure

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

| 标记                | 级别 | 描述        |
| :---------------- | :- | :-------- |
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
  only:
    - tags
```

## 配置说明

### test.yaml 配置项

| 配置项                 | 说明          | 默认值            |
| :------------------ | :---------- | :------------- |
| `env.default`       | 默认环境        | dev            |
| `servers.*.url`     | 服务地址        | -              |
| `servers.*.timeout` | 请求超时        | 30s            |
| `parallel.workers`  | 并行进程数       | 2              |
| `report.allure_dir` | Allure 报告目录 | reports/allure |

## 注意事项

1. 运行并行测试时，确保测试用例之间无共享状态
2. 生产环境测试需谨慎，建议使用独立的测试账号
3. 性能测试会产生大量请求，避免在生产环境频繁运行

## 维护人员

- 测试开发团队

## 版本历史

- v1.0.0: 初始版本
- v1.1.0: 添加数据驱动测试
- v1.2.0: 支持并行测试
- v1.3.0: 添加性能测试支持

