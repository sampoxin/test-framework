# API测试用例生成器技能

## 技能概述

本技能用于根据接口文档或 curl 命令自动生成符合项目规范的接口测试用例和测试数据。生成的代码可以直接运行在当前项目中。

## 功能特性

- **支持两种输入格式**：JSON 格式接口文档 和 curl 命令格式
- **固定断言规则**：成功断言 `code == "Success"`，失败断言 `code == "FAIL"`
- **强制 p0 用例**：每个接口至少生成1个 p0 级别的测试用例
- **自动生成多场景测试数据**：正常请求、参数缺失、参数异常等
- **自动添加测试级别标记**：p0/p1/p2/p3
- **自动生成 Allure 测试报告装饰器**
- **支持动态数据生成规则**
- **测试数据追加模式**：只追加新数据，不覆盖已存在的测试数据
- **测试文件追加模式**：文件已存在时，新测试方法追加到现有文件中

## 输入格式

### 格式一：curl 命令格式（推荐）

直接输入 curl 命令，技能会自动解析并生成测试用例：

```bash
curl -X POST https://api.example.com/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "password": "123456"}'
```

### 格式二：JSON 格式

```json
{
  "epic": "模块名称",
  "feature": "功能名称",
  "apis": [
    {
      "name": "接口名称",
      "method": "GET/POST/PUT/DELETE",
      "path": "/api/v1/xxx",
      "description": "接口描述",
      "required_params": ["param1", "param2"],
      "optional_params": ["param3"],
      "param_types": {
        "param1": "string",
        "param2": "int",
        "param3": "bool"
      }
    }
  ]
}
```

## 输出结果

### 1. 测试数据文件 (`data/test_data.json`)

```json
{
  "coupon_list": [
    {"case_name": "coupon_list-正常请求", "request_data": {"pageNum": 1, "pageSize": 10, "sort": "ASC"}, "expected_code": "Success", "mark": "p0"},
    {"case_name": "coupon_list-缺少pageNum", "request_data": {"pageSize": 10, "sort": "ASC"}, "expected_code": "FAIL", "mark": "p3"},
    {"case_name": "coupon_list-pageNum为空", "request_data": {"pageNum": "", "pageSize": 10, "sort": "ASC"}, "expected_code": "FAIL", "mark": "p3"}
  ]
}
```

### 2. 测试用例文件 (`testcases/test_coupon.py`)

```python
import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields

TEST_DATA = load_test_data("test_data.json")

@allure.epic("优惠券模块")
@allure.feature("优惠券功能")
class TestCouponList:
    @allure.story("coupon_list")
    @pytest.mark.parametrize("data", TEST_DATA["coupon_list"], ids=[x["case_name"] for x in TEST_DATA["coupon_list"]])
    def test_coupon_list(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST", "/api/v1/wx-mini/coupon/list", json=data_fields)
        assert resp.json()["code"] == data["expected_code"]
```

## 特殊参数处理规则

| 参数名        | 处理规则               | 示例值                     |
| ---------- | ------------------ | ----------------------- |
| `sort`     | 固定为 `ASC` 或 `DESC` | `ASC`                   |
| `pageNum`  | 固定测试值 `1` 和 `2`    | `1`                     |
| `pageSize` | 固定测试值 `10` 和 `20`  | `10`                    |
| `status`   | 从描述中提取枚举值          | `"1"`、`"2"`、`"4"`、`"5"` |

## 测试用例场景

每个接口自动生成以下场景：

| 场景    | 描述        | 标记     | 断言                  |
| ----- | --------- | ------ | ------------------- |
| 正常请求  | 所有参数正常    | **p0** | `code == "Success"` |
| 缺少参数  | 缺少某个必填参数  | p3     | `code == "FAIL"`    |
| 参数为空  | 必填参数为空字符串 | p3     | `code == "FAIL"`    |
| 参数为负数 | 数值类型参数为负数 | p3     | `code == "FAIL"`    |

## 命名规则

### 文件命名

- 对 URL 按 `/` 截取，取倒数第2个元素作为文件名
- 示例：`https://xxx.com/api/v1/wx-mini/coupon/list` → `test_coupon.py`

### allure 装饰器命名

- **epic**：URL 倒数第2个元素翻译为中文 + "模块"
- **feature**：URL 倒数第2个元素翻译为中文 + "功能"
- 示例：`coupon` → `@allure.epic("优惠券模块")`、`@allure.feature("优惠券功能")`

### 请求路径

- 截取 URL 中 `com` 后的内容
- 示例：`https://xxx.com/api/v1/wx-mini/coupon/list` → `/api/v1/wx-mini/coupon/list`

## 中英文翻译映射

| 英文           | 中文  |
| ------------ | --- |
| coupon       | 优惠券 |
| member       | 会员  |
| user         | 用户  |
| order        | 订单  |
| product      | 商品  |
| address      | 地址  |
| activity     | 活动  |
| payment      | 支付  |
| marketing    | 营销  |
| report       | 报告  |
| config       | 配置  |
| setting      | 设置  |
| message      | 消息  |
| notification | 通知  |
| sms          | 短信  |
| email        | 邮件  |

## 使用示例

### 示例：curl 命令输入

**输入**：

```bash
curl --location --request POST 'https://dev-ocss-gateway.youdtj.com/api/v1/wx-mini/coupon/list' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "pageNum": 1,
    "pageSize": 10,
    "sort": "ASC",
    "status": "1-未生效，2-未使用，4-已使用，5-已过期"
  }'
```

**输出**：

- 测试数据文件：`data/test_data.json`（追加 `coupon_list` 数据集）
- 测试用例文件：`testcases/test_coupon.py`

**生成的测试用例**：

```python
@allure.epic("优惠券模块")
@allure.feature("优惠券功能")
class TestCouponList:
    @allure.story("coupon_list")
    @pytest.mark.parametrize("data", TEST_DATA["coupon_list"], ids=[x["case_name"] for x in TEST_DATA["coupon_list"]])
    def test_coupon_list(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("POST", "/api/v1/wx-mini/coupon/list", json=data_fields)
        assert resp.json()["code"] == data["expected_code"]
```

## 动态数据规则

支持的动态数据生成规则：

| 规则                      | 说明           | 示例                        |
| ----------------------- | ------------ | ------------------------- |
| DYNAMIC\_text\_N        | 生成N个字符的随机文本  | DYNAMIC\_text\_20         |
| DYNAMIC\_int\_M\_N      | 生成M到N之间的随机整数 | DYNAMIC\_int\_1\_100      |
| DYNAMIC\_birthday\_M\_N | 生成M到N岁的生日日期  | DYNAMIC\_birthday\_18\_60 |
| DYNAMIC\_phone          | 生成随机手机号      | DYNAMIC\_phone            |
| DYNAMIC\_name           | 生成随机姓名       | DYNAMIC\_name             |
| DYNAMIC\_avatar         | 生成随机头像URL    | DYNAMIC\_avatar           |

## 运行测试

```bash
# 运行所有测试
pytest

# 仅运行P0级别测试
pytest -m p0

# 生成Allure报告
allure generate reports/allure-results -o reports/allure-report
```

## 追加规则

### 1. 测试数据追加规则

- 新生成的测试数据只做追加，不删除已存在的数据
- 如果数据键已存在（如 `coupon_list`），则跳过该接口的测试数据生成
- 控制台会输出警告信息：`警告：测试数据键 'xxx' 已存在，跳过追加`

### 2. 测试文件追加规则

- 如果测试文件已存在（如 `test_coupon.py`），新的测试方法会追加到该文件中
- 新方法追加到测试类内部，保持代码结构清晰
- 如果文件不存在，则创建新文件

### 3. 示例

```bash
# 第一次生成（文件不存在）
# 输出：测试用例已保存: testcases/test_coupon.py

# 第二次生成（文件已存在）  
# 输出：测试用例已追加到: testcases/test_coupon.py
```

## 注意事项

1. **固定断言**：成功场景断言 `code == "Success"`，失败场景断言 `code == "FAIL"`
2. **强制 p0**：每个接口至少包含1个 p0 级别的正常请求用例
3. **curl 解析**：支持单行和多行 curl 命令，自动识别 JSON 格式请求体
4. **参数类型自动检测**：从 curl 请求体中自动检测参数类型（int/string/date/phone）
5. **特殊参数处理**：`sort`、`pageNum`、`pageSize`、`status` 有特殊处理规则
6. **追加模式**：测试数据和测试文件均采用追加模式，不会覆盖已有内容

## 技能位置

```
skills/api_test_generator/
├── __init__.py
├── generator.py
├── templates.py
└── skill.md
```

