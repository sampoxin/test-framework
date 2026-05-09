import pytest

from api.client import ApiClient
from config.settings import DEV_URL,TIMEOUT, TENANT


@pytest.fixture(scope="session")
def client():
    client = ApiClient(DEV_URL, TIMEOUT)
    # 登录
    resp = client.send("POST",
                       "/api/v1/wx-mini/member/login/test",
                       json={"phone": "15973199394", "areaCode": "86", "registerChannel": "WX_APPLET"}
                       )
    resp_json = resp.json()
    resp_data = resp_json.get("data",{})
    assert resp_json.get("msg") =="成功"
    assert resp_data.get("phone") == "15973199394"
    client.set_token({
        "auth-token": resp_data.get("token"),
        "x-user": str({"id":resp_data.get("memberId")})
        })
    client.user_data = resp_data  # 把登录信息挂到 client 上
    yield client
    # 登出
    client.send("POST",
                "/api/v1/wx-mini/member/logout"
                )
    # client.stats()

@pytest.fixture(scope="function")
def context():
    """上下文"""
    return {}
