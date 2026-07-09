"""
后台用例专用 conftest
- 提供 admin_client fixture（后台登录）
- 提供 invoice_no fixture（发票号，单一数据源）
- 测试执行前自动清理数据，确保干净初始状态
"""
import pytest
import allure
from utils.logger import setup_logger
from utils.file_helper import FileHelper

logger = setup_logger()


@pytest.fixture(scope="session")
def fixed_data():
    """发票编号 - 全局唯一数据源，conftest和测试用例共用"""
    return {"data_1": {"invoice_nos": ["26922000000673529101"],"receipt_nos":["PO99487990000237"],"supplier_name":"宝宝兄弟(青岛)食品有限公司"},
            "data_2": {"invoice_nos": ["26312000003454746196"],"receipt_nos":["PO99487990000228"],"supplier_name":"上海英联食品饮料有限公司"},
            "data_3": {"invoice_nos": [],"receipt_nos":["PO99487990000234"],"return_nos":["RO99487990000113"],"supplier_name":"上海英联食品饮料有限公司"}
        }



@pytest.fixture(scope="class", autouse=True)
def setup_clean_data(request, fixed_data):
    """
    前置清理：每个测试类执行前触发，只清理该类用到的发票数据
    测试类需通过类属性 DATA_KEY 声明使用哪组数据（如 DATA_KEY = "data_1"）
    """
    data_key = getattr(request.cls, "DATA_KEY", None)
    print("DATA_KEY",data_key)
    if not data_key:
        logger.warning(f"[清理] {request.cls.__name__} 未声明 DATA_KEY，跳过清理")
        yield
        return

    data = fixed_data[data_key]
    invoice_nos = data.get("invoice_nos", [])

    with allure.step(f"前置数据清理 ({data_key})"):
        if invoice_nos:
            try:
                from utils.db_helper import clean_three_way_match_data
                clean_three_way_match_data(invoice_nos=invoice_nos)
                logger.info(f"[清理] {request.cls.__name__} 清理完成 invoice_nos={invoice_nos}")
            except Exception as e:
                logger.warning(f"[清理] {request.cls.__name__} 清理失败: {e}，请手动检查数据库")
        else:
            logger.info(f"[清理] {request.cls.__name__} 无发票号，跳过清理")

    yield  # 用例执行，跑完后数据保留不再清理

@pytest.fixture(scope="session")
def file_helper():
    return FileHelper()
