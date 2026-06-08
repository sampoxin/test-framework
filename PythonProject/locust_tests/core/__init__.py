"""
Core 模块

提供性能测试的核心组件：
- 负载形状定义
- 通用工具函数
"""

from locust_tests.core.load_shapes import (
    StagedLoadShape,
    WaveLoadShape,
    ConcurrencyLoadShape
)

__all__ = [
    'StagedLoadShape',
    'WaveLoadShape',
    'ConcurrencyLoadShape'
]
