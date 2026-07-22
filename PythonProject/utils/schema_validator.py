"""API 响应 Schema 校验工具

使用 jsonschema 验证 API 响应结构，防止接口静默变更导致测试假绿。

用法:
    from utils.schema_validator import validate_schema, STANDARD_RESPONSE

    # 1. 校验标准响应结构（code + data + msg）
    validate_schema(response_json, STANDARD_RESPONSE)

    # 2. 自定义 Schema
    page_schema = {
        "type": "object",
        "required": ["code", "data"],
        "properties": {
            "code": {"type": "string", "const": "Success"},
            "data": {
                "type": "object",
                "required": ["records", "total"],
                "properties": {
                    "records": {"type": "array"},
                    "total": {"type": "integer"}
                }
            }
        }
    }
    validate_schema(response_json, page_schema)
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


# ==================== 通用 Schema 定义 ====================

STANDARD_RESPONSE: Dict[str, Any] = {
    """标准 API 响应包装结构"""
    "type": "object",
    "required": ["code", "data", "msg"],
    "properties": {
        "code": {"type": "string"},
        "msg": {"type": "string"},
        "success": {"type": "boolean"},
    }
}

PAGE_RESPONSE: Dict[str, Any] = {
    """分页查询响应（data.records + data.total）"""
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["records", "total"],
            "properties": {
                "records": {"type": "array"},
                "total": {"type": "integer"},
                "current": {"type": "integer"},
                "size": {"type": "integer"},
                "pages": {"type": "integer"},
            }
        }
    }
}

BATCH_RESULT_RESPONSE: Dict[str, Any] = {
    """批量操作结果响应（successCount + failCount）"""
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["successCount", "failCount", "totalCount"],
            "properties": {
                "successCount": {"type": "integer"},
                "failCount": {"type": "integer"},
                "totalCount": {"type": "integer"},
            }
        }
    }
}


# ==================== 校验函数 ====================

def validate_schema(data: Any, schema: Dict[str, Any], context: str = "") -> None:
    """
    校验数据是否符合 JSON Schema

    Args:
        data: 待校验的响应数据
        schema: JSON Schema 定义
        context: 上下文描述（用于错误信息）

    Raises:
        SchemaValidationError: 校验失败
        ImportError: 未安装 jsonschema
    """
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
