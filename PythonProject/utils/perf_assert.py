"""API 性能基线断言工具

对 API 响应时间进行阈值断言，防止性能退化。

用法:
    from utils.perf_assert import assert_response_time

    # 在测试用例中
    result = match_api.page_matches(supplierName="xxx")
    assert_response_time(match_api.client, max_seconds=2.0, label="核票列表查询")

    # 或直接用 elapsed 值
    assert_response_time(elapsed=0.5, max_seconds=1.0, label="发票收取")
"""
import os
from typing import Optional
from utils.logger import logger


# 性能基线开关：CI 中可设 PERF_CHECK=0 关闭，本地调试设 PERF_CHECK=1 开启
PERF_CHECK_ENABLED = os.environ.get("PERF_CHECK", "1") == "1"

# 全局默认阈值（秒）
DEFAULT_MAX_SECONDS = 3.0


def assert_response_time(client_or_elapsed, max_seconds: float = DEFAULT_MAX_SECONDS,
                         label: str = "") -> None:
    """
    断言最近一次 API 请求的响应时间不超过阈值

    Args:
        client_or_elapsed: ApiClient 实例（自动取 history[-1]）或 elapsed 数值
        max_seconds: 最大允许响应时间（秒）
        label: 描述标签（用于日志和报告）

    Raises:
        AssertionError: 响应时间超阈值
    """
    if not PERF_CHECK_ENABLED:
        return

    if isinstance(client_or_elapsed, (int, float)):
        elapsed = float(client_or_elapsed)
    else:
        # ApiClient 实例，取最后一次请求的 elapsed
        history = getattr(client_or_elapsed, "history", [])
        if not history:
            logger.warning(f"[性能] 无请求历史，跳过断言: {label}")
            return
        elapsed = history[-1]["elapsed"]

    if elapsed > max_seconds:
        msg = f"[性能] {label} 响应超时: {elapsed:.3f}s > {max_seconds}s"
        logger.warning(msg)
        raise AssertionError(msg)
    else:
        logger.info(f"[性能] {label} 响应正常: {elapsed:.3f}s <= {max_seconds}s")
