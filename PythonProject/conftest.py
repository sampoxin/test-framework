import pytest
import os

from api.client import ApiClient
from config.settings import BASE_URL, TIMEOUT

TEST_USERS = [
    {"phone": "15973199394", "areaCode": "86", "registerChannel": "WX_APPLET"},
    {"phone": "12222220010", "areaCode": "86", "registerChannel": "WX_APPLET"}
]
def pytest_configure(config):
    for level in ['p0', 'p1', 'p2', 'p3']:
        config.addinivalue_line("markers", f"{level}: 测试级别")

def pytest_collection_modifyitems(config, items):
    for item in items:
        if hasattr(item, 'callspec'):
            data = item.callspec.params.get('data')
            if data and data.get('mark') in ['p0', 'p1', 'p2', 'p3']:
                    item.add_marker(getattr(pytest.mark, data.get('mark')))

@pytest.fixture(scope="session")
def client(request):
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')

    if worker_id == 'master':
        worker_id = getattr(request.config, 'worker_id', 'master')

    if worker_id == 'master':
        worker_num = os.getpid() % len(TEST_USERS)
    else:
        worker_num = int(worker_id.replace('gw', ''))

    user = TEST_USERS[worker_num % len(TEST_USERS)]
    
    client = ApiClient(BASE_URL, TIMEOUT)
    resp = client.send("POST", "/api/v1/wx-mini/member/login/test", json=user)
    resp_data = resp.json().get("data", {})
    assert resp_data.get("token"), "登录失败"
    client.set_token({
        "auth-token": resp_data.get("token"),
        "x-user": str({"id": resp_data.get("memberId")})
    })
    client.user_data = resp_data
    yield client

@pytest.fixture(scope="class")
def context():
    return {}