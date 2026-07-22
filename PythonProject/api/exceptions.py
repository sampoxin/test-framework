"""API 层自定义异常体系

异常层级:
    ApiError (基类)
    ├── HttpError      — HTTP 状态码非 200
    ├── BusinessError  — 业务码 code != Success
    └── AuthExpiredError — Token 过期（HTTP 401）
"""


class ApiError(Exception):
    """API 层基础异常"""
    pass


class HttpError(ApiError):
    """HTTP 请求失败（状态码非 200）"""

    def __init__(self, method: str, url: str, status_code: int, response_body: str = ""):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(
            f"HTTP 请求失败\n"
            f"  {method} {url}\n"
            f"  status_code={status_code}\n"
            f"  response={response_body[:500]}"
        )


class BusinessError(ApiError):
    """业务逻辑失败（code != Success）"""

    def __init__(self, method: str, url: str, code: str, msg: str = "", request_body=None):
        self.method = method
        self.url = url
        self.code = code
        self.msg = msg
        self.request_body = request_body
        super().__init__(
            f"业务失败\n"
            f"  {method} {url}\n"
            f"  code={code}\n"
            f"  msg={msg}\n"
            f"  请求体={request_body}"
        )


class AuthExpiredError(ApiError):
    """认证过期（HTTP 401 或业务 Token 失效）"""
    pass
