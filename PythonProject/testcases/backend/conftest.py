"""
后台用例专用 conftest
- 提供 admin_client fixture（后台登录）
- 提供 invoice_no fixture（发票号，单一数据源）
- 测试执行前自动清理数据，确保干净初始状态
"""
import os
import json
import pytest
import allure
from utils.logger import setup_logger
from utils.file_helper import FileHelper

logger = setup_logger()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'output')
TEST_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'test_three_way_match_data.json')


@pytest.fixture(scope="session")
def fixed_data():
    """测试数据 - 从 data/test_three_way_match_data.json 加载"""
    with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="class", autouse=True)
def setup_test_data(request, fixed_data):
    """
    通用测试数据初始化 fixture
    自动从 fixed_data 中根据测试类的 DATA_KEY 加载测试数据
    """
    # 获取测试类定义的 DATA_KEY
    data_key = getattr(request, "param", None) or getattr(request.cls, "DATA_KEY", None)
    if not data_key:
        pytest.skip("测试类未定义 DATA_KEY，跳过初始化")

    test_data = fixed_data.get(data_key)
    if not test_data:
        pytest.skip(f"fixed_data 中未找到 key: {data_key}")

    # 将测试数据设置到测试类上
    request.cls.invoice_nos = test_data.get("invoice_nos", [])
    request.cls.receipt_nos = test_data.get("receipt_nos", [])
    request.cls.return_nos = test_data.get("return_nos", [])
    request.cls.supplier_name = test_data.get("supplier_name", "")

    # 如果有发票号，默认取第一个
    if request.cls.invoice_nos:
        request.cls.invoice_no = request.cls.invoice_nos[0]


@pytest.fixture(scope="session", autouse=True)
def setup_clean_data(request):
    """
    前置清理：每个测试类执行前触发
    从 data/output 中最新的JSON文件读取 invoiceNo 进行清理
    """
    match_ids = _extract_match_ids_from_latest_file()

    with allure.step(f"前置数据清理"):
        if match_ids:
            try:
                from utils.db_helper import clean_three_way_match_data
                clean_three_way_match_data(match_ids=match_ids)
                logger.info(f"[清理]清理完成 match_ids={match_ids}")
            except Exception as e:
                logger.warning(f"[清理]清理失败: {e}，请手动检查数据库")
        else:
            logger.info(f"[清理]未找到发票号，跳过清理")

    yield  # 用例执行，跑完后数据保留不再清理


def _extract_match_ids_from_latest_file():
    """从 data/output 中最新的JSON文件提取所有 invoiceNo"""
    if not os.path.exists(OUTPUT_DIR):
        logger.info(f"[清理] 输出目录不存在: {OUTPUT_DIR}")
        return []

    json_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')], reverse=True)
    if not json_files:
        logger.info(f"[清理] 输出目录为空，无JSON文件")
        return []

    latest_file = os.path.join(OUTPUT_DIR, json_files[0])
    logger.info(f"[清理] 读取最新文件: {latest_file}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"[清理] 读取文件失败: {e}")
        return []

    if not isinstance(data, list):
        data = [data]

    match_ids = []
    for item in data:
        match_id = item.get("matchId")
        if isinstance(match_id, list):
            match_ids.extend(match_id)
        else:
            match_ids.append(match_id)

    logger.info(f"[清理] 从文件中提取到 matchIds: {match_ids}")
    return match_ids

@pytest.fixture(scope="class")
def file_helper():
    return FileHelper()


# ==================== API Object Fixtures ====================

@pytest.fixture(scope="session")
def match_api(admin_client):
    """三单匹配业务统一 API（发票 + 核票 + 强制匹配 + 操作记录）"""
    from api.three_way_match_api import ThreeWayMatchApi
    return ThreeWayMatchApi(admin_client)


@pytest.fixture(scope="session")
def context():
    """后台测试共享上下文，用于用例间传递数据（session级避免pytest-order跨类切换导致重建）"""
    return {}

if __name__ == "__main__":
    _extract_match_ids_from_latest_file()
