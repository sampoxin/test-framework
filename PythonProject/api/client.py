import time
import requests
from functools import wraps

from config.settings import TENANT
from utils.logger import setup_logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiClient:
    def __init__(self, base_url, timeout):
        self.base_url = base_url
        self.timeout = timeout
        self.history = []
        self.logger = setup_logger()

        # 保持会话
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json","x-tenant": TENANT})

        # 重试配置
        retry = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔递增：1s, 2s, 4s
            status_forcelist=[500, 502, 503]  # 这些状态码触发重试
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)


    def req_log(func):
        @wraps(func)
        def wrapper(self, method, path, **params):
            start_time = time.time()
            url = self.base_url + path
            method = method.upper()
            self.logger.info(f"开始请求: [{method}] {url} params={params}")

            try:
                response = func(self, method, url, **params)
                elapsed = time.time() - start_time
                try:
                    self.logger.info(f"[{method}] {url} 响应结果:{response.json()} 耗时:{elapsed:.3f}s")
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
    def send(self, method, url, params=None,json=None,data=None):
        # 显式参数params/json/data 分开传
        return self.session.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            timeout=self.timeout
        )

    def set_token(self, token):
        self.session.headers.update(token)

    def get_history(self):
        return self.history

    def stats(self):
        total_requests = len(self.history)
        request_count = {}
        for request in self.history:
            method = request.get("method")
            request_count[method] = request_count.get(method, 0) + 1
        for method, count in request_count.items():
            self.logger.info(f"{method}:{count}")
        self.logger.info(f"总请求数:{total_requests}")