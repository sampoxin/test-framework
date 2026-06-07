import pytest
import os
import shutil
import time
from datetime import datetime
from api.client import ApiClient
from config import BASE_URL, TIMEOUT, CURRENT_ENV
from utils.dingtalk_notifier import DingTalkNotifier

TEST_USERS = [
    {"phone": "15973199394", "areaCode": "86", "registerChannel": "WX_APPLET"},
    {"phone": "12222220010", "areaCode": "86", "registerChannel": "WX_APPLET"}
]

# 全局变量存储测试结果
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "total": 0,
    "start_time": None,
    "end_time": None
}


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
    test_results["end_time"] = time.time()
    duration = test_results["end_time"] - test_results["start_time"]

    # 发送钉钉通知
    webhook_url = os.environ.get("DINGTALK_WEBHOOK")
    print(f"[钉钉通知] WEBHOOK配置: {'已配置' if webhook_url else '未配置'}")
    if webhook_url:
        notifier = DingTalkNotifier(webhook_url=webhook_url)
        result = {
            "passed": test_results["passed"],
            "failed": test_results["failed"],
            "skipped": test_results["skipped"],
            "total": test_results["total"],
            "duration": duration,
            "env": CURRENT_ENV,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"[钉钉通知] 开始发送测试报告: 通过={result['passed']}, 失败={result['failed']}, 跳过={result['skipped']}")
        success = notifier.send_test_report(result)
        print(f"[钉钉通知] 发送结果: {'成功' if success else '失败'}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        test_results["total"] += 1
        if report.passed:
            test_results["passed"] += 1
        elif report.failed:
            test_results["failed"] += 1
        elif report.skipped:
            test_results["skipped"] += 1


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