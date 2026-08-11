import time
import requests
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from config import TENANT
from utils.logger import logger, mask_dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from api.exceptions import HttpError, BusinessError, AuthExpiredError


class ApiClient:
    def __init__(self, base_url: str, timeout: int, think_time: float = 0):
        self.base_url: str = base_url
        self.timeout: int = timeout
        self.history: List[Dict[str, Any]] = []
        self.logger = logger
        self.think_time: float = think_time

        # Token 刷新：外部设置此回调，401 时自动调用
        self._login_callback: Optional[Callable] = None

        # 保持会话
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "x-tenant": TENANT})

        # 重试配置
        retry = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔递增：1s, 2s, 4s
            status_forcelist=[500, 502, 503]  # 这些状态码触发重试
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def set_auth_callback(self, callback: Callable[["ApiClient"], None]) -> None:
        """
        设置 Token 刷新回调

        用法（conftest.py 中）:
            def refresh_token(client):
                resp = client.send("POST", "/api/v1/admin/auth/login", json={...})
                token = resp.json()["data"]["authToken"]
                client.set_token({"mmhm-token": token})

            client.set_auth_callback(refresh_token)
        """
        self._login_callback = callback

    def req_log(func):
        @wraps(func)
        def wrapper(self, method: str, path: str, **params) -> requests.Response:
            start_time = time.time()
            url = self.base_url + path
            method = method.upper()
            # 日志脱敏：请求参数（SensitiveFilter 兜底防护）
            safe_params = mask_dict(params)
            self.logger.info(f"开始请求: [{method}] {url} params={safe_params}")

            try:
                response = func(self, method, url, **params)
                elapsed = time.time() - start_time
                try:
                    # 日志脱敏：响应体（SensitiveFilter 兜底防护）
                    safe_resp = mask_dict(response.json())
                    self.logger.info(f"[{method}] {url} 响应结果:{safe_resp} 耗时:{elapsed:.3f}s")
                except ValueError:
                    self.logger.info(f"[{method}] {url} 响应非JSON 耗时:{elapsed:.3f}s")
                self.history.append({
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "elapsed": elapsed
                })
                return response
            except Exception as e:
                self.logger.error(f"[{method}] {url} 失败: {str(e)}")
                raise
        return wrapper

    @req_log
    def send(self, method: str, url: str, params: Optional[Dict] = None,
             json: Optional[Any] = None, data: Optional[Any] = None) -> requests.Response:
        """发送 HTTP 请求"""
        response = self.session.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            timeout=self.timeout
        )
        if self.think_time > 0:
            time.sleep(self.think_time)
        return response

    def send_and_validate(self, method: str, url: str, params: Optional[Dict] = None,
                          json: Optional[Any] = None, data: Optional[Any] = None) -> Dict[str, Any]:
        """
        发送请求并自动断言 status_code==200 和 code==Success，直接返回 JSON

        Raises:
            HttpError: HTTP 状态码非 200
            BusinessError: 业务码 code != Success
            AuthExpiredError: Token 过期且刷新失败
        """
        result = self.send(method, url, params=params, json=json, data=data)

        # 401 → 尝试刷新 Token 并重试
        if result.status_code == 401 and self._login_callback:
            self.logger.warning(f"[Token过期] {method} {url} → 尝试刷新Token")
            try:
                self._login_callback(self)
                result = self.send(method, url, params=params, json=json, data=data)
            except Exception as e:
                raise AuthExpiredError(f"Token 刷新失败: {e}") from e

        if result.status_code != 200:
            raise HttpError(method, url, result.status_code, result.text)

        result_json = result.json()

        # 业务 Token 失效
        if result_json.get("code") == "Unauthorized":
            if self._login_callback:
                self.logger.warning(f"[Token失效] {method} {url} → 尝试刷新Token")
                try:
                    self._login_callback(self)
                    result = self.send(method, url, params=params, json=json, data=data)
                    result_json = result.json()
                except Exception as e:
                    raise AuthExpiredError(f"Token 刷新失败: {e}") from e
            else:
                raise AuthExpiredError(f"认证过期: {method} {url}")

        if result_json["code"] != "Success":
            raise BusinessError(method, url, result_json["code"],
                                result_json.get("msg", ""), json)
        return result_json

    def set_token(self, token: Dict[str, str]) -> None:
        """设置认证 Token 到 Session Headers"""
        self.session.headers.update(token)

    def get_history(self) -> List[Dict[str, Any]]:
        """获取请求历史记录"""
        return self.history

    def stats(self) -> None:
        """输出请求统计"""
        total_requests = len(self.history)
        request_count: Dict[str, int] = {}
        for request in self.history:
            method = request.get("method")
            request_count[method] = request_count.get(method, 0) + 1
        for method, count in request_count.items():
            self.logger.info(f"{method}:{count}")
        self.logger.info(f"总请求数:{total_requests}")
