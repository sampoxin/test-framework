"""
统一日志模块

- 日志级别通过环境变量 LOG_LEVEL 控制（默认 INFO）
- 内置 SensitiveFilter 自动脱敏日志中的敏感字段
- 提供 mask_dict / mask_value 工具函数供其他模块显式调用
"""
import logging
import os
import re
from datetime import datetime
from typing import Any
from logging.handlers import TimedRotatingFileHandler

# 日志级别通过环境变量 LOG_LEVEL 控制，默认 INFO
# 可选值: DEBUG / INFO / WARNING / ERROR
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


# ==================== 敏感字段定义 ====================

SENSITIVE_KEYS = frozenset({
    "password", "authToken", "token", "secret",
    "mmhm-token", "auth-token", "x-user", "authorization",
    "ADMIN_PASSWORD", "DB_PASSWORD",
})

_SENSITIVE_KEYS_LOWER = {k.lower() for k in SENSITIVE_KEYS}

# 预编译正则：匹配日志消息中的敏感键值对
# 示例: 'password': 'MyS3cret'  /  password=MyS3cret  /  "authToken": "abc"
_SENSITIVE_PATTERN = re.compile(
    r"""(['"]?)(""" +
    "|".join(re.escape(k) for k in sorted(SENSITIVE_KEYS, key=len, reverse=True)) +
    r""")\1(\s*[:=]\s*)(['"]?)(.+?)\4(?=[,}\s\])])""",
    re.IGNORECASE
)


# ==================== 脱敏工具函数 ====================

def mask_value(value: Any) -> str:
    """对敏感值脱敏：保留前2后2字符"""
    if isinstance(value, str) and len(value) > 6:
        return value[:2] + "***" + value[-2:]
    return "***"


def mask_dict(obj: Any) -> Any:
    """递归脱敏 dict/list 中的敏感字段"""
    if isinstance(obj, dict):
        return {
            k: mask_value(v) if k.lower() in _SENSITIVE_KEYS_LOWER else mask_dict(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [mask_dict(item) for item in obj]
    return obj


# ==================== 日志过滤器 ====================

class SensitiveFilter(logging.Filter):
    """
    自动脱敏日志过滤器

    两层防护：
    1. record.args 中的 dict 对象 → 递归脱敏
    2. record.msg（已格式化字符串）→ 正则匹配敏感键值对并替换
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # 处理 % 格式化参数中的 dict
        if record.args:
            if isinstance(record.args, dict):
                record.args = mask_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    mask_dict(a) if isinstance(a, (dict, list)) else a
                    for a in record.args
                )

        # 处理已格式化的消息字符串
        if isinstance(record.msg, str):
            record.msg = _SENSITIVE_PATTERN.sub(self._replace_match, record.msg)

        return True

    @staticmethod
    def _replace_match(m: re.Match) -> str:
        quote = m.group(1)
        key = m.group(2)
        sep = m.group(3)
        value = m.group(5)
        masked = mask_value(value)
        return f"{quote}{key}{quote}{sep}{quote}{masked}{quote}"


# ==================== Logger 工厂 ====================

def setup_logger(name=None):
    _logger = logging.getLogger(name or __name__)
    if not _logger.handlers:
        _logger.setLevel(getattr(logging, _LOG_LEVEL, logging.INFO))
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

        log_dir = os.path.join(os.path.dirname(__file__), '..', 'log')
        os.makedirs(log_dir, exist_ok=True)

        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'{date_str}.log')

        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='D',
            interval=1,
            backupCount=30,
            encoding='utf-8',
            delay=False
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = '%Y-%m-%d.log'
        file_handler.addFilter(SensitiveFilter())
        _logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(SensitiveFilter())
        _logger.addHandler(console_handler)

        _logger.propagate = False
    return _logger


logger = setup_logger()
