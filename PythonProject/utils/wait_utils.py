"""轮询等待工具 - 替代硬编码 time.sleep

使用示例:
    # 等待某个条件成立
    result = wait_until(
        lambda: api.page_matches(invoiceNo="xxx")["data"]["rows"],
        timeout=10,
        interval=1,
        desc="等待核票匹配完成"
    )

    # 等待状态变更
    wait_until(
        lambda: get_status() == "MATCHED",
        timeout=15,
        interval=2,
        desc="等待状态变为 MATCHED"
    )
"""
import time
from utils.logger import logger


class WaitTimeoutError(Exception):
    """轮询超时异常"""
    pass


def wait_until(condition, timeout: int = 10, interval: float = 1.0,
               desc: str = "等待条件成立", raise_on_timeout: bool = True):
    """
    轮询等待条件成立，替代硬编码 sleep

    Args:
        condition: 可调用对象，返回 truthy 值表示条件满足
        timeout: 最大等待秒数
        interval: 轮询间隔秒数
        desc: 描述信息（用于日志）
        raise_on_timeout: 超时时是否抛异常（False 则返回最后结果）

    Returns:
        condition() 的返回值（最后一次调用结果）

    Raises:
        WaitTimeoutError: 超时且 raise_on_timeout=True
    """
    start = time.time()
    last_result = None

    while time.time() - start < timeout:
        try:
            last_result = condition()
            if last_result:
                elapsed = time.time() - start
                logger.info(f"[等待] {desc} 完成 (耗时 {elapsed:.1f}s)")
                return last_result
        except Exception as e:
            logger.debug(f"[等待] {desc} 条件检查异常: {e}")

        time.sleep(interval)

    elapsed = time.time() - start
    msg = f"[等待] {desc} 超时 (已等 {elapsed:.1f}s > {timeout}s)"
    logger.warning(msg)

    if raise_on_timeout:
        raise WaitTimeoutError(msg)
    return last_result
