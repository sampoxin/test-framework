"""API 响应 Schema 校验工具（jsonschema），防止接口静默变更导致测试假绿。

分层设计（基于运营端接口日志实测结构）:
    第 1 层 通用包装: STANDARD_RESPONSE / wrap() / page_of()
    第 2 层 通用形态: PAGE / BATCH_RESULT / LIST_DATA / OBJECT_DATA / BOOL_DATA
    第 3 层 业务定制: LOGIN / THREE_WAY_MATCH_PAGE / THREE_WAY_MATCH_DETAIL / ITEM_CODE

设计原则:
    - Schema 只管结构（字段存在 + 类型）；业务成败（code==Success）由
      ApiClient.send_and_validate 断言并抛 BusinessError，这里不重复锁定
    - required 只放每次响应都出现且用例依赖的字段；不加 additionalProperties: false
    - 金额一律 "number"（实测有 int/float 漂移）；可空字段一律 ["类型", "null"]
    - 不要在 dict 字面量内写 docstring，会与下一行 key 隐式拼接
"""
from typing import Dict, Any
from utils.logger import logger

try:
    from jsonschema import validate, ValidationError, SchemaError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class SchemaValidationError(Exception):
    """响应 Schema 校验失败"""
    pass


# ==================== 第 1 层：通用包装 ====================

def wrap(data_schema: Dict[str, Any] = None) -> Dict[str, Any]:
    """把 data 层 Schema 包进标准响应包装；不传则 data 形态不限"""
    return {
        "type": "object",
        "required": ["code", "success", "data"],
        "properties": {
            "code": {"type": "string"},
            "success": {"type": "boolean"},
            "msg": {"type": "string"},
            "errorMsg": {"type": "string"},
            "data": data_schema or {},
        },
    }


def page_of(record_schema: Dict[str, Any] = None) -> Dict[str, Any]:
    """分页形态：records + total/size/current/pages（MyBatis-Plus 风格）"""
    return wrap({
        "type": "object",
        "required": ["records", "total", "current", "size"],
        "properties": {
            "records": {"type": "array", "items": record_schema or {"type": "object"}},
            "total":   {"type": "integer", "minimum": 0},
            "size":    {"type": "integer", "minimum": 0},
            "current": {"type": "integer", "minimum": 1},
            "pages":   {"type": "integer", "minimum": 0},
        },
    })


# ==================== 第 2 层：通用形态 ====================
STANDARD_RESPONSE = wrap()                            # 只校包装层，data 不限
PAGE_RESPONSE = page_of()                             # 分页，不校 record 内部
LIST_DATA_RESPONSE = wrap({"type": "array"})          # data 为纯数组
OBJECT_DATA_RESPONSE = wrap({"type": "object"})       # data 为对象，不校内部
BOOL_DATA_RESPONSE = wrap({"type": "boolean"})        # data 为布尔

# 批量操作结果：batchAudit/audit/cancel/approval-batch/push-settlement-batch 等
BATCH_RESULT_RESPONSE = wrap({
    "type": "object",
    "required": ["successCount", "failCount"],
    "properties": {
        "successCount": {"type": "integer", "minimum": 0},
        "failCount":    {"type": "integer", "minimum": 0},
        "totalCount":   {"type": "integer", "minimum": 0},
        "failDetails":  {"type": "array"},
    },
})


# ==================== 第 3 层：业务 Schema ====================
LOGIN_RESPONSE = wrap({
    "type": "object",
    "required": ["authToken", "tenantId", "expireIn"],
    "properties": {
        "authToken": {"type": "string", "minLength": 1},
        "tenantId":  {"type": "integer"},
        "expireIn":  {"type": "integer", "minimum": 0},
    },
})

# 三单匹配分页 record：只锁关键字段
THREE_WAY_MATCH_RECORD = {
    "type": "object",
    "required": ["id", "invoiceNo", "supplierName", "invoiceAmount", "auditStatus"],
    "properties": {
        "id":            {"type": "integer"},
        "invoiceNo":     {"type": "string"},
        "supplierName":  {"type": "string"},
        "invoiceAmount": {"type": "number"},
        "auditStatus":   {"type": "integer"},
        "matchStatus":   {"type": ["integer", "null"]},
        "orderNo":       {"type": ["string", "null"]},
        "settleNo":      {"type": ["string", "null"]},
    },
}
THREE_WAY_MATCH_PAGE_RESPONSE = page_of(THREE_WAY_MATCH_RECORD)

THREE_WAY_MATCH_DETAIL_RESPONSE = wrap({
    "type": "object",
    "required": ["id", "invoiceId", "invoiceNo", "supplierName", "invoiceAmount"],
    "properties": {
        "id":            {"type": "integer"},
        "invoiceId":     {"type": "integer"},
        "invoiceNo":     {"type": "string"},
        "supplierName":  {"type": "string"},
        "invoiceAmount": {"type": "number"},
        "matchStatus":   {"type": ["integer", "null"]},
        "items":         {"type": ["array", "null"]},
    },
})

# 编辑商品代码结果（只有 successCount，不能复用 BATCH_RESULT_RESPONSE）
ITEM_CODE_RESPONSE = wrap({
    "type": "object",
    "required": ["successCount", "updatedItems"],
    "properties": {
        "successCount":  {"type": "integer", "minimum": 0},
        "updatedItems":  {"type": "array"},
        "notFoundItems": {"type": "array"},
    },
})


def validate_schema(data: Any, schema: Dict[str, Any], context: str = "") -> None:
    """校验数据是否符合 JSON Schema，失败抛 SchemaValidationError（含错误路径）"""
    if not HAS_JSONSCHEMA:
        logger.warning("[Schema] jsonschema 未安装，跳过校验。请执行: pip install jsonschema")
        return

    try:
        validate(instance=data, schema=schema)
        logger.debug(f"[Schema] 校验通过: {context}")
    except ValidationError as e:
        msg = f"[Schema] 响应结构校验失败: {context}\n  路径: {list(e.absolute_path)}\n  错误: {e.message}"
        logger.error(msg)
        raise SchemaValidationError(msg) from e
    except SchemaError as e:
        msg = f"[Schema] Schema 定义错误: {e.message}"
        logger.error(msg)
        raise SchemaValidationError(msg) from e
