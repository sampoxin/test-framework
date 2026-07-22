## 项目简介

多端自动化测试工程，覆盖 **后台接口测试**、**后台管理系统 UI 测试**、**微信小程序测试** 和 **Locust 性能测试**，基于 pytest 统一运行。

---

## 目录结构

```
PythonProject/
├── api/                          # API 层
│   ├── client.py                 #   ApiClient - HTTP 传输层（session/重试/token）
│   ├── base_api.py               #   BaseApi - API Object 基类
│   └── three_way_match_api.py    #   ThreeWayMatchApi - 三单匹配业务 API（29个方法）
│
├── config/                       # 配置层
│   ├── __init__.py               #   统一导出入口
│   └── environments.py           #   多环境配置（dev/test/pre/prod）
│
├── utils/                        # 工具层
│   ├── logger.py                 #   日志
│   ├── db_helper.py              #   MySQL 数据库操作
│   ├── file_helper.py            #   文件读写
│   ├── dingtalk_notifier.py      #   钉钉通知
│   ├── assemble_data.py          #   数据组装
│   └── tools.py                  #   通用工具
│
├── testcases/                    # 测试用例
│   ├── backend/                  #   后台接口测试（三单匹配/强制匹配/批量匹配）
│   │   ├── conftest.py           #     测试数据 + API Object fixture + 数据清理
│   │   ├── test_three_way_match.py
│   │   ├── test_force_match.py
│   │   ├── test_force_receive_invoice.py
│   │   └── test_batch_match.py
│   ├── web/                      #   后台管理系统 UI 测试（Playwright）
│   │   └── test_receipt_invoice.py
│   ├── miniapp/                  #   小程序测试（Minium）
│   │   ├── test_personal.py
│   │   └── test_user_info.py
│   └── Client/                   #   C端接口测试（活动/优惠券/会员）
│
├── mini/                         # 小程序 Minium 配置
│   ├── config.json               #   Minium 运行配置
│   ├── suite.json                #   测试套件
│   └── pages/                    #   Page Object
│
├── locust_tests/                 # Locust 性能测试
│   ├── locustfile.py
│   ├── core/                     #   负载模型
│   └── tasks/                    #   任务定义
│
├── data/                         # 测试数据
│   ├── test_data.json
│   └── output/                   #   测试产出数据（用于数据清理）
│
├── scripts/                      # 脚本工具
│   └── generate_report.py        #   Locust 报告生成
│
├── conftest.py                   # 全局 conftest（登录/通知/Allure）
├── pytest.ini                    # pytest 配置
├── run.py                        # 统一运行入口
└── requirements.txt
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 运行测试

```bash
# 运行全部用例（backend + miniapp + web）
python run.py

# 仅运行后台接口测试
python run.py backend

# 仅运行小程序测试
python run.py miniapp

# 仅运行后台管理系统 UI 测试
python run.py web

# 透传 pytest 参数
python run.py web --slowmo=0          # Web 测试关闭慢速
python run.py backend -v --tb=long    # 详细输出
```

也可以直接用 pytest：

```bash
pytest testcases/backend/ -v                    # 后台接口
pytest testcases/web/ -v                        # Web UI
pytest testcases/miniapp/ -v --no-cov           # 小程序（需禁用 coverage）
pytest -m p0 -v                                 # 仅冒烟
```

### 3. 切换环境

通过环境变量 `LOCUST_ENV` 切换，默认 `dev`：

```bash
# Windows PowerShell
$env:LOCUST_ENV="test"; python run.py backend

# Linux/Mac
LOCUST_ENV=test python run.py backend
```

| 环境 | 说明 |
|------|------|
| `dev` | 开发环境（默认） |
| `test` | 测试环境 |
| `pre` | 预发环境 |
| `prod` | 生产环境（谨慎） |

### 4. 查看报告

```bash
# Allure 报告
allure serve reports/allure-results

# 覆盖率报告（自动生成到 htmlcov/）
open htmlcov/index.html
```

---

## 后台接口测试

### 架构分层

```
ApiClient          → HTTP 传输层（session、重试、token、日志）
  └─ BaseApi       → API Object 基类（统一 GET/POST）
       └─ ThreeWayMatchApi  → 业务 API（29 个方法）
```

- `api/client.py` — 底层 HTTP 客户端，负责连接管理、自动重试（500/502/503）、请求日志
- `api/base_api.py` — API Object 基类，提供 `_get()` / `_post()` 语义化入口
- `api/three_way_match_api.py` — 业务层，封装发票管理、核票匹配、强制匹配、操作记录全部接口

### 测试用例

| 文件 | 场景 | 用例数 |
|------|------|--------|
| `test_three_way_match.py` | 人工匹配：收票→核票→匹配→推送结算 | 8 |
| `test_force_match.py` | 强制匹配：收票→强制匹配→推送结算 | 6 |
| `test_force_receive_invoice.py` | 强制收票：收/退货单→生成发票→推送结算 | 5 |
| `test_batch_match.py` | 批量操作：批量收票→批量审核→批量匹配→批量推送 | 7 |

### Fixture 体系

```python
match_api    # session 级，ThreeWayMatchApi 实例（统一业务 API）
context      # session 级，用例间共享数据字典
fixed_data   # session 级，测试数据源（发票号/收退货单号/供应商）
file_helper  # session 级，写入 data/output 用于数据清理
```

---

## Web UI 测试（Playwright）

基于 Playwright + Ant Design 组件库，控件统一通过 **唯一 id** 定位。

```bash
python run.py web                       # 正常运行
python run.py web --slowmo=0            # CI 模式（无延迟）
python run.py web --slowmo=2000         # 调试模式（慢放观察）
```

`--slowmo` 默认 1000ms（pytest.ini 全局配置），命令行可覆盖。

---

## 小程序测试（Minium）

### 运行方式

```bash
# pytest 模式（推荐）
python run.py miniapp

# Minium 原生模式
python -m minium.framework.loader -c mini/config.json -s mini/suite.json
```

### 注意事项

- 小程序测试包含 Minium 线程，**必须加 `--no-cov`** 避免卡死（run.py 已自动处理）
- 用例执行顺序由方法名前缀控制（`test_01_` → `test_02_`），Minium 不支持 pytest-order
- 每个用例前默认重启小程序（`config.json` 中 `auto_relaunch` 控制）

---

## Locust 性能测试

### 运行

```bash
# Web UI 模式
locust -f locust_tests/locustfile.py --host=https://dev-ocss-gateway.youdtj.com

# 无头模式（CI/CD）
locust -f locust_tests/locustfile.py --headless -u 100 -r 10 -t 5m

# 生成报告
python scripts/generate_report.py locust_tests/locustfile.py https://dev-ocss-gateway.youdtj.com
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-f` | 测试脚本 | `-f locust_tests/locustfile.py` |
| `--headless` | 无界面模式 | |
| `-u` | 虚拟用户数 | `-u 100` |
| `-r` | 每秒启动用户数 | `-r 10` |
| `-t` | 持续时间 | `-t 5m` |
| `--host` | 目标主机 | `--host=https://api.example.com` |

---

## 钉钉通知

测试完成后自动推送结果到钉钉群。

### 配置

```bash
# Windows PowerShell
$env:DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"
$env:DINGTALK_SECRET="SECxxx"    # 加签模式（可选）

# Linux/Mac
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"
```

GitHub Actions 中在 Settings → Secrets 添加 `DINGTALK_WEBHOOK` 即可。

### 通知效果

- 通过：绿色报告
- 失败：红色报告，@所有人

---

## CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest testcases/backend/ -m p0 --tb=short
        env:
          DINGTALK_WEBHOOK: ${{ secrets.DINGTALK_WEBHOOK }}
```

---

## 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.p0` | 冒烟测试，核心功能 |
| `@pytest.mark.p1` | 核心测试，主要流程 |
| `@pytest.mark.p2` | 功能测试，次要功能 |
| `@pytest.mark.p3` | 边界测试，边缘场景 |
| `@pytest.mark.skip_login` | 跳过小程序自动登录 |
