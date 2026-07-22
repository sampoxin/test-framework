"""API Object 基类 - 所有 API 服务类的公共父类"""
from utils.logger import logger


class BaseApi:
    """
    API Object 基类

    提供统一的 GET/POST 调用入口，底层委托 ApiClient.send_and_validate
    自动断言 status_code==200 和 code==Success，直接返回 JSON dict
    """

    def __init__(self, client):
        self.client = client

    def _get(self, path: str, **kwargs) -> dict:
        """发送 GET 请求并返回 JSON"""
        logger.info(f"[{self.__class__.__name__}] GET {path}")
        return self.client.send_and_validate("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> dict:
        """发送 POST 请求并返回 JSON"""
        logger.info(f"[{self.__class__.__name__}] POST {path}")
        return self.client.send_and_validate("POST", path, **kwargs)
