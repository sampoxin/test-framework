# 多端自动化测试工程

基于 **pytest** 统一驱动的多端自动化测试框架，覆盖后台接口测试、后台管理系统 UI 测试（Playwright）、微信小程序测试（Minium）、C 端接口测试与 Locust 性能测试。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [目录结构](#目录结构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [测试模块](#测试模块)
- [测试报告](#测试报告)
- [测试通知（钉钉 / 企业微信）](#测试通知钉钉--企业微信)
- [CI/CD 集成](#cicd-集成)
- [测试标记](#测试标记)
- [常见问题](#常见问题)

---

## 功能特性

- **多端覆盖**：后台接口 / 后台管理 UI / 小程序 UI / 小程序接口 / 性能测试，统一入口运行
- **API Object 分层**：`ApiClient`（传输层）→ `BaseApi`（基类）→ 业务 API，职责清晰
- **企业级质量加固**：业务层重试、jsonschema 响应校验、性能基线断言、失败自动重跑
- **可观测性**：Allure 报告、覆盖率报告、日志脱敏、失败截图、钉钉通知
- **数据闭环**：测试产出数据落盘 `data/output/`，支持自动化数据清理

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 测试框架 | pytest | 9.0.2 |
| Web UI | playwright / pytest-playwright | 1.61.0 / 0.8.0 |
| 小程序 | minium | 1.6.0 |
| 性能测试 | locust | 2.24.0 |
| 报告 | allure-pytest | 2.16.0 |
| 数据库 | PyMySQL | 1.2.0 |
| 数据校验 | jsonschema | 4.26.0 |
| 其他 | requests / Faker / python-dotenv | - |

## 目录结构

```
PythonProject/
├── api/                          # API 层
│   ├── client.py                 #   ApiClient - HTTP 传输层（session/重试/token）
│   ├── base_api.py               #   BaseApi - API Object 基类
│   ├── exceptions.py             #   自定义异常
│   ├── three_way_match_api.py    #   ThreeWayMatchApi - 三单匹配业务 API
│   └── miniapp_client_api.py     #   MiniappClientApi - 小程序 C 端业务 API
│
├── config/                       # 配置层
│   ├── __init__.py               #   统一导出入口
│   └── environments.py           #   多环境配置（dev/test/pre/prod）
│
├── utils/                        # 工具层
│   ├── logger.py                 #   日志（含敏感信息脱敏）
│   ├── db_helper.py              #   MySQL 数据库操作
│   ├── file_helper.py            #   文件读写
│   ├── dingtalk_notifier.py      #   钉钉通知
│   ├── wecom_notifier.py         #   企业微信通知
│   ├── assemble_data.py          #   数据组装
│   ├── schema_validator.py       #   jsonschema 响应结构校验
│   ├── perf_assert.py            #   响应时间性能基线断言
│   ├── wait_utils.py             #   等待工具
│   └── tools.py                  #   通用工具
│
├── testcases/                    # 测试用例
│   ├── backend/                  #   后台接口测试
│   │   ├── conftest.py           #     测试数据 + API Object fixture + 数据清理
│   │   ├── test_three_way_match.py
│   │   ├── test_force_match.py
│   │   ├── test_force_receive_invoice.py
│   │   ├── test_batch_match.py
│   │   └── test_batch_settlement.py
│   ├── web/                      #   后台管理系统 UI 测试（Playwright）
│   │   ├── conftest.py           #     浏览器/登录 fixture
│   │   ├── test_login.py
│   │   └── test_receipt_invoice.py
│   ├── miniapp/                  #   小程序 UI 测试（Minium）
│   │   ├── conftest.py           #     自动登录/失败熔断
│   │   ├── test_login.py
│   │   ├── test_personal.py
│   │   └── test_user_info.py
│   └── mini_client/              #   小程序 C 端接口测试
│       ├── conftest.py
│       ├── test_member.py        #     会员
│       ├── test_activity.py      #     活动
│       ├── test_coupon.py        #     优惠券
│       └── test_marketing.py     #     营销
│
├── mini/                         # 小程序 Minium 配置
│   ├── config.json               #   Minium 运行配置
│   ├── suite.json                #   测试套件
│   ├── conftest.py
│   ├── common/                   #   通用操作
│   └── pages/                    #   Page Object
│
├── web/                          # Web 端 Page Object
│   ├── pages/                    #   页面对象
│   ├── components/               #   组件封装（侧边栏等）
│   └── utils/                    #   UI 断言等工具
│
├── locust_tests/                 # Locust 性能测试
│   ├── locustfile.py
│   ├── core/                     #   负载模型
│   └── tasks/                    #   任务定义
│
├── data/                         # 测试数据
│   ├── test_three_way_match_data.json    # 三单匹配测试数据
│   ├── test_mini_api_data.json           # 小程序接口测试数据
│   ├── dev_member_data.csv               # 会员数据
│   └── output/                           # 测试产出数据（用于数据清理）
│
├── scripts/                      # 脚本工具
│   └── generate_report.py        #   Locust 报告生成
│
├── conftest.py                   # 全局 conftest（登录/通知/Allure）
├── pytest.ini                    # pytest 配置
├── run.py                        # 统一运行入口
├── .env                          # 敏感配置（不提交 Git）
└── requirements.txt              # 依赖清单
```

## 环境要求

- Python 3.12+
- 微信开发者工具（小程序测试需要，开启服务端口）
- Allure CLI（查看测试报告，可选）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件（参考下方[配置说明](#配置说明)）。

### 3. 运行测试

```bash
# 运行全部用例（backend + miniapp + web + mini_client）
python run.py

# 按模块运行
python run.py backend        # 后台接口测试
python run.py web            # 后台管理系统 UI 测试
python run.py miniapp        # 小程序 UI 测试
python run.py mini_client    # 小程序 C 端接口测试

# 透传 pytest 参数（以 - 开头的参数会透传给 pytest）
python run.py web --slowmo=0                 # Web 测试关闭慢速（CI 模式）
python run.py web --slowmo=1500              # 调试模式（慢放观察）
python run.py backend --api-think-time=500   # API 请求后等待 500 毫秒
python run.py backend -v --tb=long           # 详细输出
```

也可以直接用 pytest：

```bash
pytest testcases/backend/ -v                # 后台接口
pytest testcases/web/ -v                    # Web UI
pytest testcases/miniapp/ -v --no-cov       # 小程序（需禁用 coverage）
pytest testcases/mini_client/ -v            # C 端接口
pytest -m p0 -v                             # 仅冒烟
```

## 配置说明

### 敏感配置（.env）

敏感信息统一放在项目根目录 `.env` 文件中（**不要提交到 Git**）：

```ini
# 后台管理员账号
ADMIN_ACCOUNT=<账号>
ADMIN_PASSWORD=<加密密码>
ADMIN_PASSWORD_CIPHER=<明文密码>

# 数据库（开发环境）
DB_HOST=<数据库地址>
DB_PORT=3306
DB_USER=<用户名>
DB_PASSWORD=<密码>
DB_NAME=<库名>

# 测试用户
TEST_USER_PHONE=<手机号>
TEST_USER_PHONE_2=<手机号>

# 钉钉通知（可选）
DINGTALK_WEBHOOK=
DINGTALK_SECRET=

# 企业微信通知（可选）
WECOM_WEBHOOK=
```

### 多环境切换

通过环境变量 `LOCUST_ENV` 切换运行环境，默认 `dev`：

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

## 测试模块

### 后台接口测试（testcases/backend）

**架构分层**：

```
ApiClient          → HTTP 传输层（session、重试、token、日志）
  └─ BaseApi       → API Object 基类（统一 GET/POST、Allure 步骤、业务层重试）
       └─ ThreeWayMatchApi   → 三单匹配业务 API
       └─ MiniappClientApi   → 小程序 C 端业务 API
```

**测试用例**：

| 文件 | 场景 |
|------|------|
| `test_three_way_match.py` | 人工匹配：收票 → 核票 → 匹配 → 推送结算 |
| `test_force_match.py` | 强制匹配：收票 → 强制匹配 → 推送结算 |
| `test_force_receive_invoice.py` | 强制收票：收/退货单 → 生成发票 → 推送结算 |
| `test_batch_match.py` | 批量操作：批量收票 → 批量审核 → 批量匹配 → 批量推送 |
| `test_batch_settlement.py` | 批量推送结算单：混合匹配（强制 + 人工）流程 |

**Fixture 体系**：

```python
match_api    # session 级，ThreeWayMatchApi 实例（统一业务 API）
context      # session 级，用例间共享数据字典
fixed_data   # session 级，测试数据源（发票号/收退货单号/供应商）
file_helper  # session 级，写入 data/output 用于数据清理
```

### Web UI 测试（testcases/web）

基于 Playwright + Ant Design 组件库，控件统一通过 **唯一 id** 精准定位。

```bash
python run.py web                # 正常运行（--slowmo 默认 1000ms）
python run.py web --slowmo=0     # CI 模式（无延迟）
python run.py web --slowmo=2000  # 调试模式（慢放观察）
```

`--slowmo` 默认值配置在 `testcases/web/conftest.py`，命令行传参可覆盖。

### 小程序测试（testcases/miniapp）

```bash
# pytest 模式（推荐）
python run.py miniapp

# Minium 原生模式
python -m minium.framework.loader -c mini/config.json -s mini/suite.json
```

注意事项：

- 小程序测试包含 Minium 线程，**必须加 `--no-cov`** 避免卡死（`run.py` 已自动处理）
- 用例执行顺序由方法名前缀控制（`test_01_` → `test_02_`），Minium 不支持 pytest-order
- 每个用例前默认重启小程序（`mini/config.json` 中 `auto_relaunch` 控制）
- 登录测试用例使用 `@pytest.mark.skip_login` 跳过自动登录

### 小程序 C 端接口测试（testcases/mini_client）

覆盖会员、活动、优惠券、营销等 C 端业务接口，基于 `MiniappClientApi` API Object 封装。

```bash
python run.py mini_client
python run.py mini_client --api-think-time=500   # 请求间隔 500ms
```

### Locust 性能测试（locust_tests）

```bash
# Web UI 模式
locust -f locust_tests/locustfile.py --host=https://dev-ocss-gateway.youdtj.com

# 无头模式（CI/CD）
locust -f locust_tests/locustfile.py --headless -u 100 -r 10 -t 5m

# 生成报告
python scripts/generate_report.py locust_tests/locustfile.py https://dev-ocss-gateway.youdtj.com
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `-f` | 测试脚本 | `-f locust_tests/locustfile.py` |
| `--headless` | 无界面模式 | |
| `-u` | 虚拟用户数 | `-u 100` |
| `-r` | 每秒启动用户数 | `-r 10` |
| `-t` | 持续时间 | `-t 5m` |
| `--host` | 目标主机 | `--host=https://api.example.com` |

## 测试报告

```bash
# Allure 报告（结果自动写入 reports/allure-results）
allure serve reports/allure-results

# 覆盖率报告（自动生成到 htmlcov/）
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

## 测试通知（钉钉 / 企业微信）

测试完成后自动推送结果到钉钉群或企业微信群，消息采用 4 块结构：
1. **标题**：执行的模块名 + 环境 + 整体结果
2. **执行指标**：总用例 / 成功 / 失败 / 跳过 / 通过率 / 耗时
3. **模块统计**：按模块（后端接口 / 小程序接口 / 小程序UI / Web UI）拆分
4. **失败用例**：最多列 5 条失败用例

通过为绿色报告；失败为红色报告，钉钉会 @所有人。

在 `.env` 或系统环境变量中配置（两个渠道独立，配哪个就推哪个）：

```bash
# Windows PowerShell
$env:DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"
$env:DINGTALK_SECRET="SECxxx"    # 加签模式（可选）
$env:WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

# Linux/Mac
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"
export WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
```

GitHub Actions 中在 Settings → Secrets 添加 `DINGTALK_WEBHOOK` / `WECOM_WEBHOOK` 即可。

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

## 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.p0` | 冒烟测试，核心功能 |
| `@pytest.mark.smoke` | 冒烟测试用例 |
| `@pytest.mark.web` | 后台管理系统 UI 测试 |
| `@pytest.mark.flaky` | 不稳定用例（自动重试） |
| `@pytest.mark.skip_login` | 跳过小程序自动登录（登录测试用例专用） |

## 常见问题

**Q: 小程序测试卡死不动？**
A: 确认微信开发者工具已打开并开启服务端口；同时必须携带 `--no-cov`（`run.py` 已自动处理）。

**Q: Web 测试执行太快看不清？**
A: 使用 `python run.py web --slowmo=2000` 慢放观察。

**Q: 接口测试请求过快被限流？**
A: 使用 `--api-think-time=500` 控制每次请求后的等待时间（单位毫秒）。
