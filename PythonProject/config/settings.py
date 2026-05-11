import os

ENV = os.environ.get("TEST_ENV", "dev")
CONFIG = {
    "dev": {"url": "https://dev-ocss-gateway.youdtj.com", "timeout": 30},
    "test": {"url": "https://dev-ocss-gateway.youdtj.com", "timeout": 30},
    "prod": {"url": "https://prod-ocss-gateway.youdtj.com", "timeout": 30}
}

BASE_URL = CONFIG[ENV]["url"]
TIMEOUT = CONFIG[ENV]["timeout"]
TENANT = "1"