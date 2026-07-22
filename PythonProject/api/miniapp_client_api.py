"""
小程序端（mini_client）API Object 集合

包含 4 个业务 API 类：
- ActivityApi: 营销活动
- CouponApi: 优惠券
- MarketingApi: 问卷活动
- MemberApi: 会员管理
"""
from typing import Dict, List, Optional

from api.base_api import BaseApi


class ActivityApi(BaseApi):
    """营销活动 API"""

    _PREFIX = "/api/v1/wx-mini/marketing/activity"

    def get_detail(self, member_id: int, activity_id: int) -> dict:
        """获取活动详情"""
        return self._post(f"{self._PREFIX}/detail",
                          json={"memberId": member_id, "activityId": activity_id})

    def get_prize_details(self, member_id: int, activity_id: int) -> dict:
        """获取活动奖品详情"""
        return self._post(f"{self._PREFIX}/prize-details",
                          json={"memberId": member_id, "activityId": activity_id})

    def record_visit(self, member_id: int, activity_id: int) -> dict:
        """记录活动访问"""
        return self._post(f"{self._PREFIX}/visit",
                          json={"memberId": member_id, "activityId": activity_id})

    def get_times(self, member_id: int, activity_id: int) -> dict:
        """查询活动参与次数"""
        return self._post(f"{self._PREFIX}/times",
                          json={"memberId": member_id, "activityId": activity_id})

    def check_condition(self, member_id: int, activity_id: int) -> dict:
        """检查活动参与条件"""
        return self._post(f"{self._PREFIX}/check",
                          json={"memberId": member_id, "activityId": activity_id})

    def join(self, member_id: int, activity_id: int) -> dict:
        """参与活动"""
        return self._post(f"{self._PREFIX}/join",
                          json={"memberId": member_id, "activityId": activity_id})


class CouponApi(BaseApi):
    """优惠券 API"""

    _PREFIX = "/api/v1/wx-mini/coupon"

    def count_user_coupons(self, status_list: List[int]) -> dict:
        """获取用户优惠券数量"""
        return self._post(f"{self._PREFIX}/countUserCoupons",
                          json={"statusList": status_list})

    def list_coupons(self, **filters) -> dict:
        """获取优惠券列表"""
        return self._post(f"{self._PREFIX}/list", json=filters)

    def get_details(self, coupon_id: int) -> dict:
        """获取优惠券详情"""
        return self._post(f"{self._PREFIX}/details", json={"id": coupon_id})

    def get_city_list(self, template_id: int) -> dict:
        """查询优惠券适用城市"""
        return self._post(f"{self._PREFIX}/cityList", json={"templateId": template_id})

    def get_store_list(self, template_id: int, city_code: str) -> dict:
        """查询优惠券适用门店"""
        return self._post(f"{self._PREFIX}/storeList",
                          json={"templateId": template_id, "cityCode": city_code})

    def get_goods_scope(self, template_id: int) -> dict:
        """查询优惠券适用商品"""
        return self._post(f"{self._PREFIX}/goodsScope", json={"templateId": template_id})


class MarketingApi(BaseApi):
    """问卷活动 API"""

    _PREFIX = "/api/v1/wx-mini/marketing/questionnaire"

    def get_detail(self, questionnaire_id: int, openid: str,
                   unionid: str, member_id: int) -> dict:
        """获取问卷详情"""
        return self._post(f"{self._PREFIX}/detail", json={
            "questionnaireId": questionnaire_id,
            "openid": openid,
            "unionid": unionid,
            "memberId": member_id
        })

    def submit(self, questionnaire_id: int, openid: str, unionid: str,
               member_id: int, item_list: List[dict]) -> dict:
        """提交问卷"""
        return self._post(f"{self._PREFIX}/submit", json={
            "questionnaireId": questionnaire_id,
            "openid": openid,
            "unionid": unionid,
            "memberId": member_id,
            "itemList": item_list
        })

    def get_review(self, openid: str, page_num: int = 1, page_size: int = 10) -> dict:
        """获取问卷点评"""
        return self._post(f"{self._PREFIX}/review", json={
            "openid": openid,
            "pageNum": page_num,
            "pageSize": page_size
        })


class MemberApi(BaseApi):
    """会员管理 API"""

    _PREFIX = "/api/v1/wx-mini/member"

    def get_profile(self) -> dict:
        """获取会员信息"""
        return self._get(f"{self._PREFIX}/profile")

    def check_update_birthday(self) -> dict:
        """检查是否可以更新生日"""
        return self._get(f"{self._PREFIX}/checkUpdateBirthday")

    def get_tag_info(self, member_type: int) -> dict:
        """查询会员标签"""
        return self._get(f"{self._PREFIX}/tag/info/{member_type}")

    def update(self, member_id: int, **fields) -> dict:
        """更新会员信息"""
        return self._post(f"{self._PREFIX}/update",
                          json={"memberId": member_id, **fields})

    def get_le_meng_card(self) -> dict:
        """查询乐檬会员卡余额"""
        return self._get(f"{self._PREFIX}/queryLeMengCard")

    def get_le_meng_deposit(self, **data) -> dict:
        """查询乐檬存款记录"""
        return self._post(f"{self._PREFIX}/queryLeMengDeposit", json=data)

    def get_le_meng_consume(self, **data) -> dict:
        """查询乐檬消费记录"""
        return self._post(f"{self._PREFIX}/queryLeMengConsume", json=data)

    def get_pay_token(self, open_id: str) -> dict:
        """获取微信支付组件 token"""
        return self._get(f"{self._PREFIX}/pay-view/{open_id}")

    def get_rule(self) -> dict:
        """查看会员规则"""
        return self._get(f"{self._PREFIX}/rule")

    def check_tag_filled(self) -> dict:
        """查询会员是否填写完标签"""
        return self._get(f"{self._PREFIX}/tag/checkFilled")

    def cancel(self, member_id: int, verify_code: str,
               is_member_cancel: bool = True) -> dict:
        """注销会员"""
        return self._post(f"{self._PREFIX}/cancel", json={
            "memberId": member_id,
            "verifyCode": verify_code,
            "isMemberCancel": is_member_cancel
        })
