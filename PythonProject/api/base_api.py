"""API Object 基类 - 所有 API 服务类的公共父类"""
import time
import allure
from typing import Callable, Dict, Any, Optional, Tuple, Type
from utils.logger import logger
from utils.schema_validator import validate_schema
from api.exceptions import BusinessError


class BaseApi:
    """
    API Object 基类

    提供统一的 GET/POST 调用入口，底层委托 ApiClient.send_and_validate
    自动断言 status_code==200 和 code==Success，直接返回 JSON dict
    所有 API 调用自动标注 Allure 步骤
    """

    def __init__(self, client: "ApiClient"):
        self.client = client

    def _get(self, path: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """发送 GET 请求并返回 JSON，可选 schema 校验"""
        step_name = f"[{self.__class__.__name__}] GET {path}"
        logger.info(step_name)
        with allure.step(step_name):
            result = self.client.send_and_validate("GET", path, **kwargs)
            if schema:
                validate_schema(result, schema, context=f"GET {path}")
            return result

    def _post(self, path: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """发送 POST 请求并返回 JSON，可选 schema 校验"""
        step_name = f"[{self.__class__.__name__}] POST {path}"
        logger.info(step_name)
        with allure.step(step_name):
            result = self.client.send_and_validate("POST", path, **kwargs)
            if schema:
                validate_schema(result, schema, context=f"POST {path}")
            return result

    def _retry(self, func: Callable, retries: int = 3, delay: float = 1.0,
               on_exceptions: Tuple[Type[Exception], ...] = (BusinessError,)) -> object:
        """
        业务层重试 - 适用于幂等操作的瞬时失败

        用法:
            result = self._retry(lambda: self.page_matches(invoiceNo="xxx"))
            result = self._retry(lambda: api.get_detail(id, sid), retries=5, delay=2)

        Args:
            func: 无参可调用对象（通常用 lambda 包装）
            retries: 最大重试次数
            delay: 重试间隔（秒）
            on_exceptions: 触发重试的异常类型
        """
        for attempt in range(1, retries + 1):
            try:
                return func()
            except on_exceptions as e:
                if attempt == retries:
                    raise
                logger.warning(f"[重试] 第{attempt}/{retries}次失败: {e}，{delay}s 后重试...")
                time.sleep(delay)
