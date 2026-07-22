"""
小程序端接口测试公共 fixture

提供：
- context: 用例间数据共享字典
- activity_api / coupon_api / marketing_api / member_api: API Object 实例
"""
import pytest
from api.miniapp_client_api import ActivityApi, CouponApi, MarketingApi, MemberApi


@pytest.fixture
def context():
    """用例间数据共享（替代全局变量）"""
    return {}


@pytest.fixture
def activity_api(client) -> ActivityApi:
    """营销活动 API"""
    return ActivityApi(client)


@pytest.fixture
def coupon_api(client) -> CouponApi:
    """优惠券 API"""
    return CouponApi(client)


@pytest.fixture
def marketing_api(client) -> MarketingApi:
    """问卷活动 API"""
    return MarketingApi(client)


@pytest.fixture
def member_api(client) -> MemberApi:
    """会员管理 API"""
    return MemberApi(client)
