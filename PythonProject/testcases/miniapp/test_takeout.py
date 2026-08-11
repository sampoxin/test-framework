"""
外送页功能测试

覆盖业务点：
    1. 分类的切换
    2. banner 左右滑动
    3. 商品列表上下滑动
    4. 从商品列表进入商品详情
    5. 商品详情上下滑动
    6. 数量加减并添加购物车
    7. 选择地址（不添加地址，只做切换）
    8. 查看购物车
    9. 在购物车加减数量
    10. 清空购物车
    11. 分别从列表和购物车提交订单
"""
import time

import pytest
import allure
from testcases.miniapp.base_test import MiniAppBase
from mini.pages.takeout_page import TakeoutPage
from mini.pages.good_detail_page import GoodsDetailPage
from utils.logger import logger


@allure.story("外送页")
class TestMiniTakeout(MiniAppBase):
    """外送页功能测试（分类/banner/商品列表/详情/地址/购物车/下单）"""

    def setUp(self):
        self.takeout_page = TakeoutPage(self)
        self.goods_detail_page = GoodsDetailPage(self)

    # ================= 工具方法 =================

    def _ensure_at_takeout(self):
        """确保当前在外送页（供依赖前序用例状态的用例兜底）"""
        if not self.takeout_page.is_at_takeout_page():
            self.takeout_page.open()
            self.takeout_page.wait_for_page(self.takeout_page.PATH, timeout=10)
            time.sleep(1)

    def _require_goods(self):
        """商品列表为空时跳过用例"""
        if self.takeout_page.is_show_empty_tip() or self.takeout_page.get_goods_count() == 0:
            pytest.skip("当前分类下暂无商品，跳过用例")

    # ================= 用例 =================

    @pytest.mark.order(30)
    @allure.step("进入外送页")
    def test_01_enter_takeout_page(self):
        """进入外送页，验证页面标题"""
        logger.info("进入外送页")
        self.takeout_page.open()
        assert self.takeout_page.wait_for_page(self.takeout_page.PATH, timeout=10), "外送页加载超时"
        time.sleep(1)
        assert self.takeout_page.is_show_takeout_title(), "外送页标题不正确"

    @pytest.mark.order(31)
    @allure.step("banner左右滑动")
    def test_02_swipe_banner(self):
        """banner 轮播左右滑动，验证当前下标变化"""
        logger.info("banner左右滑动")
        self._ensure_at_takeout()
        if not self.takeout_page.is_show_banner():
            pytest.skip("未配置 banner 轮播，跳过用例")

        origin = self.takeout_page.get_banner_current()
        # 向右滑动到下一张
        self.takeout_page.swipe_banner_to(origin + 1)
        right = self.takeout_page.get_banner_current()
        logger.info(f"banner 右滑: {origin} -> {right}")
        # 向左滑回原位置
        self.takeout_page.swipe_banner_to(origin)
        left = self.takeout_page.get_banner_current()
        logger.info(f"banner 左滑: {right} -> {left}")
        assert left == origin, f"banner 左滑未回到原位置: {left}"

    @pytest.mark.order(32)
    @allure.step("切换分类")
    def test_03_switch_category(self):
        """左侧分类切换，验证高亮分类变化"""
        logger.info("切换分类")
        self._ensure_at_takeout()
        names = self.takeout_page.get_category_names()
        logger.info(f"分类列表: {names}")
        if len(names) < 2:
            pytest.skip("分类不足 2 个，无法验证切换")

        assert self.takeout_page.is_exist_category_active(), "应存在默认选中分类"
        old_active = self.takeout_page.get_active_category_name()

        # 切换到另一个分类
        target_index = 1 if old_active == names[0] else 0
        self.takeout_page.switch_category_by_index(target_index)
        new_active = self.takeout_page.get_active_category_name()
        logger.info(f"分类切换: {old_active} -> {new_active}")
        assert new_active == names[target_index], f"分类切换失败，当前高亮: {new_active}"
        assert new_active != old_active, "切换后高亮分类未变化"

        # 按名称切回原分类
        self.takeout_page.switch_category_by_name(old_active)
        assert self.takeout_page.get_active_category_name() == old_active, "按名称切回分类失败"

    @pytest.mark.order(33)
    @allure.step("商品列表上下滑动")
    def test_04_scroll_goods_list(self):
        """商品列表向下滑动再回顶，验证滚动位置变化"""
        logger.info("商品列表上下滑动")
        self._ensure_at_takeout()
        self._require_goods()

        origin_top = self.takeout_page.get_goods_scroll_top()
        self.takeout_page.scroll_goods_list(600)
        down_top = self.takeout_page.get_goods_scroll_top()
        logger.info(f"列表下滑: {origin_top} -> {down_top}")
        assert down_top > origin_top, "商品列表向下滑动失败"

        self.takeout_page.scroll_goods_list_to_top()
        top = self.takeout_page.get_goods_scroll_top()
        logger.info(f"列表回顶: {down_top} -> {top}")
        assert top < down_top, "商品列表回顶失败"

    @pytest.mark.order(34)
    @allure.step("选择地址（仅切换）")
    def test_05_switch_address(self):
        """打开地址弹层切换到非当前选中的地址，验证顶部地址栏更新后再切回原地址"""
        logger.info("选择地址（仅切换）")
        self._ensure_at_takeout()
        old_address = self.takeout_page.get_address_text()
        has_selected = not self.takeout_page.is_show_address_placeholder()
        logger.info(f"当前地址: {old_address}（已选: {has_selected}）")

        self.takeout_page.open_address_popup()
        assert self.takeout_page.is_address_popup_visible(), "地址选择弹层未弹出"

        card_texts = self.takeout_page.get_address_card_texts()
        card_count = len(card_texts)
        if self.takeout_page.is_show_empty_address() or card_count < 2:
            self.takeout_page.close_address_popup()
            pytest.skip("账号下暂无收货地址或仅有一个地址且已选中，跳过切换")

        # 定位当前选中地址对应的卡片下标（未选地址时为 None）
        current_index = None
        if has_selected and old_address:
            for i, text in enumerate(card_texts):
                if old_address in text:
                    current_index = i
                    break
        logger.info(f"当前选中地址对应卡片下标: {current_index}")

        # 选取一个非当前选中的地址作为切换目标
        target_index = next((i for i in range(card_count) if i != current_index), None)

        # 切换到目标地址（选中后弹层自动关闭）
        self.takeout_page.select_address(target_index)
        new_address = self.takeout_page.get_address_text()
        logger.info(f"切换地址: {old_address} -> {new_address}")
        assert not self.takeout_page.is_show_address_placeholder(), "选择地址后仍显示占位文本"
        if has_selected:
            assert new_address != old_address, "切换到非当前地址后顶部地址栏未变化"

        # 切回原地址（原本已有选中地址时）
        if current_index is not None:
            self.takeout_page.open_address_popup()
            self.takeout_page.select_address(current_index)
            back_address = self.takeout_page.get_address_text()
            logger.info(f"切回原地址: {new_address} -> {back_address}")
            assert back_address == old_address, f"未能切回原地址: {back_address} != {old_address}"

    @pytest.mark.order(35)
    @allure.step("从商品列表进入商品详情")
    def test_06_open_goods_detail_from_list(self):
        """点击列表商品卡片，验证跳转商品详情页且商品名一致"""
        logger.info("从商品列表进入商品详情")
        self._ensure_at_takeout()
        self._require_goods()

        goods_name = self.takeout_page.get_goods_name(0)
        logger.info(f"点击商品: {goods_name}")
        detail_page = self.takeout_page.open_goods_detail_from_list(0)
        assert detail_page.is_at_goods_detail_page(), "未跳转到商品详情页"
        detail_title = detail_page.get_goods_title()
        logger.info(f"详情页商品标题: {detail_title}")
        assert detail_title == goods_name, f"详情页商品与列表不一致: {detail_title} != {goods_name}"

    @pytest.mark.order(36)
    @allure.step("商品详情上下滑动")
    def test_07_scroll_goods_detail(self):
        """商品详情页向下滑动到详情区，再回顶"""
        logger.info("商品详情上下滑动")
        # 依赖上一用例停留在详情页，异常时兜底重新进入
        if not self.goods_detail_page.is_at_goods_detail_page():
            self._ensure_at_takeout()
            self._require_goods()
            self.takeout_page.open_goods_detail_from_list(0)
        assert self.goods_detail_page.is_at_goods_detail_page(), "未在商品详情页"

        self.goods_detail_page.scroll_to_detail_section()
        self.goods_detail_page.scroll_detail(0)
        assert self.goods_detail_page.is_at_goods_detail_page(), "详情页滑动后页面异常"

    @pytest.mark.order(37)
    @allure.step("详情页数量加减并添加购物车")
    def test_08_add_to_cart_from_detail(self):
        """详情页数量 +/- 后加购，验证购物车角标增加，返回外送页"""
        logger.info("详情页数量加减并添加购物车")
        if not self.goods_detail_page.is_at_goods_detail_page():
            self._ensure_at_takeout()
            self._require_goods()
            self.takeout_page.open_goods_detail_from_list(0)
        assert self.goods_detail_page.is_at_goods_detail_page(), "未在商品详情页"

        if not self.goods_detail_page.is_add_cart_enabled():
            self.goods_detail_page.to_back()
            pytest.skip(f"商品不可加购: {self.goods_detail_page.get_add_cart_btn_text()}")

        # 数量加减：1 -> 2 -> 3 -> 2
        origin_qty = self.goods_detail_page.get_pick_qty()
        self.goods_detail_page.increase_qty().increase_qty()
        assert self.goods_detail_page.get_pick_qty() == origin_qty + 2, "详情页数量+失败"
        self.goods_detail_page.decrease_qty()
        pick_qty = self.goods_detail_page.get_pick_qty()
        assert pick_qty == origin_qty + 1, "详情页数量-失败"

        # 加购并验证数量
        self.goods_detail_page.add_to_cart()
        assert self.takeout_page.wait_for_page(self.takeout_page.PATH, timeout=5), "未返回外送页"
        badge = self.takeout_page.get_cart_badge_count()
        assert badge == pick_qty, "加购后购物车角标不正确"

    @pytest.mark.order(38)
    @allure.step("查看购物车")
    def test_09_view_cart(self):
        """展开悬浮购物车弹窗，验证商品行与角标一致"""
        logger.info("查看购物车")
        self._ensure_at_takeout()
        if not self.takeout_page.is_cart_visible():
            pytest.skip("购物车为空（悬浮购物车未显示），跳过用例")
        badge = self.takeout_page.get_cart_badge_count()
        self.takeout_page.open_cart()

        assert self.takeout_page.is_cart_expanded(), "购物车弹窗未展开"
        total_qty = self.takeout_page.calc_cart_total_qty()
        total_amount = self.takeout_page.calc_cart_amount()
        total = self.takeout_page.get_cart_total_amount()
        qty = self.takeout_page.get_cart_total_qty()
        logger.info(f"购物车角标: {badge}, 合计金额: {total}")
        assert badge == total_qty == qty, "购物车弹窗内商品数量与角标不一致"
        assert total_amount == total, "购物车弹窗内合计金额与计算结果不一致"

    @pytest.mark.order(39)
    @allure.step("购物车内加减数量")
    def test_10_change_cart_qty(self):
        """购物车弹窗内 +/- 修改数量，验证角标变化"""
        logger.info("购物车内加减数量")
        self._ensure_at_takeout()
        if not self.takeout_page.is_cart_visible():
            pytest.skip("购物车为空，跳过用例")
        self.takeout_page.open_cart()

        badge_before = self.takeout_page.get_cart_badge_count()
        self.takeout_page.change_cart_qty(0, delta=1)
        badge_plus = self.takeout_page.get_cart_badge_count()
        logger.info(f"购物车+1: {badge_before} -> {badge_plus}")
        assert badge_plus == badge_before + 1, "购物车内数量+失败"

        self.takeout_page.change_cart_qty(0, delta=-1)
        badge_minus = self.takeout_page.get_cart_badge_count()
        logger.info(f"购物车-1: {badge_plus} -> {badge_minus}")
        assert badge_minus == badge_before, "购物车内数量-失败"

    @pytest.mark.order(40)
    @allure.step("从购物车提交订单")
    def test_11_checkout_from_cart(self):
        """展开购物车后点「选好了」，验证跳转确认订单页后返回"""
        logger.info("从购物车提交订单")
        self._ensure_at_takeout()
        if not self.takeout_page.is_cart_visible():
            pytest.skip("购物车为空，跳过用例")

        self.takeout_page.open_cart()
        assert self.takeout_page.is_cart_expanded(), "购物车弹窗未展开"
        self.takeout_page.checkout()
        assert self.takeout_page.is_at_confirm_order_page(), "未跳转到确认订单页"

        # 返回外送页，不实际下单
        self.takeout_page.to_back()
        assert self.takeout_page.wait_for_page(self.takeout_page.PATH, timeout=5), "未返回外送页"
    #
    # @pytest.mark.order(41)
    # @allure.step("从列表加购并提交订单")
    # def test_12_checkout_from_list(self):
    #     """列表加购商品后直接点悬浮购物车「选好了」提交订单"""
    #     logger.info("从列表加购并提交订单")
    #     self._ensure_at_takeout()
    #     self._require_goods()
    #
    #     # 列表加购一件商品（悬浮购物车保持收起态）
    #     self.takeout_page.close_cart()
    #     qty_before = self.takeout_page.get_goods_qty_in_list(0)
    #     self.takeout_page.add_goods_to_cart_from_list(0)
    #     qty_after = self.takeout_page.get_goods_qty_in_list(0)
    #     logger.info(f"列表加购: {qty_before} -> {qty_after}")
    #     assert qty_after == qty_before + 1, "列表加购失败"
    #     assert self.takeout_page.is_cart_visible(), "加购后悬浮购物车未显示"
    #
    #     # 不展开弹窗，直接从悬浮购物车条提交
    #     self.takeout_page.checkout()
    #     assert self.takeout_page.is_at_confirm_order_page(), "未跳转到确认订单页"
    #
    #     self.takeout_page.to_back()
    #     assert self.takeout_page.wait_for_page(self.takeout_page.PATH, timeout=5), "未返回外送页"
    #
    # @pytest.mark.order(42)
    # @allure.step("清空购物车")
    # def test_13_clear_cart(self):
    #     """清空购物车，验证悬浮购物车消失（兼作环境清理）"""
    #     logger.info("清空购物车")
    #     self._ensure_at_takeout()
    #     if not self.takeout_page.is_cart_visible():
    #         pytest.skip("购物车已为空，跳过用例")
    #
    #     self.takeout_page.clear_cart()
    #     assert not self.takeout_page.is_cart_visible(), "清空后悬浮购物车仍显示"
