import pytest
import os
import shutil
import time
from datetime import datetime
from api.client import ApiClient
from config import BASE_URL, TIMEOUT, CURRENT_ENV
from utils.dingtalk_notifier import DingTalkNotifier
from utils.wecom_notifier import WeComNotifier

TEST_USERS = [
    {"phone": os.environ.get("TEST_USER_PHONE"), "areaCode": "86", "registerChannel": "WX_APPLET"},
    {"phone": os.environ.get("TEST_USER_PHONE_2"), "areaCode": "86", "registerChannel": "WX_APPLET"}
]

# 全局变量存储测试结果
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "total": 0,
    "start_time": None,
    "end_time": None,
    "categories": set(),  # 执行的测试类型（后端接口/小程序接口/小程序UI/Web UI），用于标题
    "modules": {},        # 按用例类统计 {类名: {"passed": 0, "failed": 0, "skipped": 0, "total": 0}}
    "failed_cases": []    # 失败用例 nodeid 列表
}

# 模块目录 -> 展示名称
MODULE_NAMES = {
    "backend": "后端接口",
    "mini_client": "小程序接口",
    "miniapp": "小程序UI",
    "web": "Web UI"
}


def _get_module_name(nodeid: str) -> str:
    """从用例 nodeid 解析所属模块名称（按用例类拆分，1个类为1个模块）"""
    normalized = nodeid.replace("\\", "/")
    segments = normalized.split("::")

    # pytest nodeid 形式：path/to/test_file.py::TestClass::test_method
    # 优先取类名作为模块
    if len(segments) >= 2 and segments[1].startswith("Test"):
        return segments[1]

    # 无类名时回退到目录映射
    return _get_category_name(nodeid)


def _get_category_name(nodeid: str) -> str:
    """从用例 nodeid 解析所属测试类型（按目录映射，用于标题）"""
    parts = nodeid.replace("\\", "/").split("/")
    if parts[0] == "testcases" and len(parts) > 1:
        key = parts[1]
    else:
        key = parts[0]
    key = key.split("::")[0]
    return MODULE_NAMES.get(key, key)


def pytest_addoption(parser):
    """注册 API 请求思考时间参数，仅影响纯 API 测试"""
    parser.addoption(
        "--api-think-time",
        action="store",
        default=0,
        type=float,
        help="每次 API 请求后等待的毫秒数（如 500 表示 0.5 秒），仅对 ApiClient 生效"
    )


def pytest_configure(config):
    # 每次测试开始前清空 allure-results 目录
    results_dir = "reports/allure-results"
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    for level in ['p0', 'p1', 'p2', 'p3']:
        config.addinivalue_line("markers", f"{level}: 测试级别")


def pytest_sessionstart(session):
    """测试会话开始时记录时间"""
    test_results["start_time"] = time.time()


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时发送通知"""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    
    # 只在 master 进程发送通知，避免 worker 进程重复发送
    if worker_id != 'master':
        print(f"[通知] 当前为 worker 进程 {worker_id}，跳过发送通知")
        return
    
    # 如果没有收集到任何测试结果，说明是 xdist 的空 session，跳过
    if test_results["total"] == 0:
        print(f"[通知] 未收集到测试结果，跳过发送")
        return
    
    test_results["end_time"] = time.time()
    duration = test_results["end_time"] - test_results["start_time"]

    # 发送钉钉通知
    webhook_url = os.environ.get("DINGTALK_WEBHOOK")
    webhook_secret = os.environ.get("DINGTALK_SECRET")
    print(f"[钉钉通知] WEBHOOK配置: {'已配置' if webhook_url else '未配置'}")
    print(f"[钉钉通知] 加签密钥: {'已配置' if webhook_secret else '未配置'}")

    # 发送企业微信通知
    wecom_webhook = os.environ.get("WECOM_WEBHOOK")
    print(f"[企业微信通知] WEBHOOK配置: {'已配置' if wecom_webhook else '未配置'}")

    # 构造通知结果数据（钉钉 / 企业微信共用）
    # 标题按测试类型聚合（后端接口 / 小程序接口 / 小程序UI / Web UI）
    categories = list(test_results["categories"])
    test_name = "、".join(categories) if categories else "未知模块"
    result = {
        "title": f"{test_name}自动化测试",
        "passed": test_results["passed"],
        "failed": test_results["failed"],
        "skipped": test_results["skipped"],
        "total": test_results["total"],
        "duration": duration,
        "env": CURRENT_ENV,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modules": test_results["modules"],
        "failed_cases": test_results["failed_cases"]
    }
    print(f"[通知] 开始发送测试报告: 通过={result['passed']}, 失败={result['failed']}, 跳过={result['skipped']}")

    if webhook_url:
        dingtalk = DingTalkNotifier(webhook_url=webhook_url, secret=webhook_secret)
        success = dingtalk.send_test_report(result)
        print(f"[钉钉通知] 发送结果: {'成功' if success else '失败'}")

    # if wecom_webhook:
    #     wecom = WeComNotifier(webhook_url=wecom_webhook)
    #     success = wecom.send_test_report(result)
    #     print(f"[企业微信通知] 发送结果: {'成功' if success else '失败'}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果"""
    outcome = yield
    report = outcome.get_result()

    # call 阶段：正常执行（通过/失败）的用例
    # setup 阶段 + skipped：@pytest.mark.skip 标记的用例（setup 阶段即跳过，无 call 报告）
    should_count = (report.when == 'call') or (report.when == 'setup' and report.skipped)
    if should_count:
        test_results["total"] += 1

        module = _get_module_name(report.nodeid)
        test_results["categories"].add(_get_category_name(report.nodeid))
        mod_stat = test_results["modules"].setdefault(
            module, {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        )
        mod_stat["total"] += 1

        if report.passed:
            test_results["passed"] += 1
            mod_stat["passed"] += 1
        elif report.failed:
            test_results["failed"] += 1
            mod_stat["failed"] += 1
            # 记录失败用例名称（取用例函数名部分）
            case_name = report.nodeid.split("::")[-1]
            test_results["failed_cases"].append(f"[{module}] {case_name}")
        elif report.skipped:
            test_results["skipped"] += 1
            mod_stat["skipped"] += 1


def pytest_collection_modifyitems(config, items):
    for item in items:
        if hasattr(item, 'callspec'):
            data = item.callspec.params.get('data')
            if data and data.get('mark') in ['p0', 'p1', 'p2', 'p3']:
                item.add_marker(getattr(pytest.mark, data.get('mark')))


def admin_login(client):
    """管理员登录（同时作为 auth_callback 供 Token 过期时自动刷新）"""
    resp = client.send("POST", "/api/v1/admin/auth/login", json={
        "account": os.environ.get("ADMIN_ACCOUNT", ""),
        "password": os.environ.get("ADMIN_PASSWORD", ""),
        "grantType": "pwd"
    })
    resp_data = resp.json().get("data", {})
    assert resp_data.get("authToken"), "后台管理员登录失败，请检查 .env 中 ADMIN_ACCOUNT/ADMIN_PASSWORD"
    client.set_token({
        "mmhm-token": resp_data.get("authToken"),
        "x-tenant": str(resp_data.get("tenantId"))
    })


def user_login(client, user):
    """前端用户登录（同时作为 auth_callback 供 Token 过期时自动刷新）"""
    resp = client.send("POST", "/api/v1/wx-mini/member/login/test", json=user)
    resp_data = resp.json().get("data", {})
    assert resp_data.get("token"), "登录失败"
    client.set_token({
        "auth-token": resp_data.get("token"),
        "x-user": str({"id": resp_data.get("memberId")})
    })
    client.user_data = resp_data


@pytest.fixture(scope="session")
def client(request):
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    think_time = float(request.config.getoption("--api-think-time", default=0)) / 1000.0

    if worker_id == 'master':
        worker_id = getattr(request.config, 'worker_id', 'master')

    if worker_id == 'master':
        worker_num = os.getpid() % len(TEST_USERS)
    else:
        worker_num = int(worker_id.replace('gw', ''))

    user = TEST_USERS[worker_num % len(TEST_USERS)]

    client = ApiClient(BASE_URL, TIMEOUT, think_time=think_time)
    user_login(client, user)
    # Token 过期时自动刷新
    client.set_auth_callback(lambda c: user_login(c, user))
    yield client

@pytest.fixture(scope="session")
def admin_client(request):
    think_time = float(request.config.getoption("--api-think-time", default=0)) / 1000.0
    client = ApiClient(BASE_URL, TIMEOUT, think_time=think_time)
    admin_login(client)
    # Token 过期时自动刷新
    client.set_auth_callback(admin_login)
    yield client

