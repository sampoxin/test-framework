"""
    商品详情页 Page Object
"""
import time
from typing import Any

import allure
from .base_page import BasePage
from utils.logger import logger


class GoodsDetailPage(BasePage):
    """商品详情页（外卖）"""
    PATH = "/packages/takeout/goodsDetail/index"

    SCROLL = ".scroll_YxUbg"
    MAIN_SWIPER = ".swiper_Bmmfj"
    TITLE = ".title_kjHqX"
    QTY_MINUS = ".qtyMinus_lNhql"
    QTY_PLUS = ".qtyPlus_qSxLm"
    QTY_NUM = ".qtyNum_RExVw"
    DETAIL_SECTION = ".detailSection_L3FCM"
    PRICE_NUM = ".priceNum_woU3K"
    ADD_CART_BTN = ".addCartBtn_wyxxt"
    CART_COUNT_BADGE = ".cartCountBadge_YIxDS"

    def __init__(self, mini: Any) -> None:
        super().__init__(mini)

    @allure.step("打开商品详情页: {spu_id}")
    def open(self, spu_id: str) -> "GoodsDetailPage":
        """按 spuId 直接跳转商品详情页"""
        self.navigate_to(f"{self.PATH}?id={spu_id}")
        return self

    @allure.step("返回上一页")
    def to_back(self) -> "GoodsDetailPage":
        """返回上一页"""
        self.go_back()
        return self

    def is_at_goods_detail_page(self) -> bool:
        return "goodsDetail" in self.get_page_path()

    def get_goods_title(self) -> str:
        """获取商品标题"""
        return self.get_text(self.TITLE)

    def get_price(self) -> str:
        """获取底部价格文本"""
        return self.get_text(self.PRICE_NUM)

    # ========== 数量选择 ==========

    def get_pick_qty(self) -> int:
        """获取当前选择数量"""
        try:
            return int(self.get_text(self.QTY_NUM))
        except (TypeError, ValueError):
            return 1

    @allure.step("详情页数量+1")
    def increase_qty(self) -> "GoodsDetailPage":
        self.tap(self.QTY_PLUS)
        return self

    @allure.step("详情页数量-1")
    def decrease_qty(self) -> "GoodsDetailPage":
        self.tap(self.QTY_MINUS)
        return self

    # ========== 加购 ==========

    def get_add_cart_btn_text(self) -> str:
        """获取加购按钮文案（添加到购物车/已售罄/已下架）"""
        return self.get_text(self.ADD_CART_BTN)

    def is_add_cart_enabled(self) -> bool:
        """加购按钮是否可点（按文案判断）"""
        return "购物车" in self.get_add_cart_btn_text()

    @allure.step("详情页加购商品")
    def add_to_cart(self) -> "GoodsDetailPage":
        """点击「添加到购物车」（需已登录且已选地址）"""
        self.tap(self.ADD_CART_BTN)
        time.sleep(2)
        return self

    def get_cart_badge_count(self) -> int:
        """获取加购按钮上的购物车角标数量"""
        try:
            return int(self.get_text(self.CART_COUNT_BADGE))
        except (TypeError, ValueError):
            return 0

    # ========== 页面滑动 ==========

    @allure.step("详情页滑动到: y={y}")
    def scroll_detail(self, y: int = 800) -> "GoodsDetailPage":
        """详情页上下滑动（y>0 向下滚动，y=0 回顶）"""
        scroll_view = self.find_element(self.SCROLL)
        if scroll_view:
            scroll_view.scroll_to(0, y)
            time.sleep(1)
        return self

    @allure.step("详情页滚动到商品详情区")
    def scroll_to_detail_section(self) -> "GoodsDetailPage":
        """滚动到「商品详情」区域

        优先用基类 call_func(scrollIntoView) 方案；
        若失败则降级为计算详情区在 scroll-view 中的偏移量，用 scroll_to 滚动。
        """
        try:
            self.scroll_to_view(self.DETAIL_SECTION)
            # 简单校验是否真的动了：避免 scroll_to_view 降级为 scroll_to(0,0) 导致未生效
            section = self.find_element(self.DETAIL_SECTION)
            if section is not None:
                try:
                    top = section.offset.get("top", None)
                    if top is not None and top < 0:
                        # 元素在视口上方（说明 scroll_to_view 没起作用），降级偏移滚动
                        logger.info(f"scroll_to_view 未生效（offset.top={top}），降级 scroll_to")
                        self._scroll_detail_by_offset(-int(top) + 200)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"滚动到详情区失败: {e}，降级 scroll_to")
            self.scroll_detail(600)
        time.sleep(1)
        return self

    def _scroll_detail_by_offset(self, y: int) -> "GoodsDetailPage":
        """按偏移量滚动详情页的 scroll-view"""
        scroll_view = self.find_element(self.SCROLL)
        if scroll_view:
            scroll_view.scroll_to(0, y)
        return self

    @allure.step("详情页主图轮播滑动到第{index}张")
    def swipe_main_swiper_to(self, index: int) -> "GoodsDetailPage":
        """顶部主图轮播左右滑动"""
        swiper = self.find_element(self.MAIN_SWIPER)
        if swiper:
            swiper.swipe_to(index)
            time.sleep(1)
        return self
