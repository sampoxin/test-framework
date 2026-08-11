"""
    外卖页 Page Object
"""
import time
from typing import Any, Dict, List

import allure
from .base_page import BasePage
from .good_detail_page import GoodsDetailPage
from utils.logger import logger


class TakeoutPage(BasePage):
    """外卖页"""
    PATH = "/pages/takeout/index"
    CONFIRM_ORDER_PATH = "/packages/takeout/confirmOrder/index"

    # ========== 顶部 / 地址栏 ==========
    TOP_TITLE = ".topTitle_TdEmU"
    ADDRESS_MAIN = ".addressMain_YM4C8"
    ADDRESS_TEXT = ".addressText_Uj4sn"
    STORE_NAME = ".storeName_VXllM"

    # ========== banner 轮播 ==========
    BANNER = ".banner_N4Zrh"
    BANNER_SWIPER = ".bannerSwiper_yijNE"

    # ========== 左侧分类导航 ==========
    CATEGORY_NAV = ".categoryNav_H5S92"
    CATEGORY_ITEM = ".catItem_oF_RZ"
    CATEGORY_ACTIVE = ".catActive_gvT2s"
    CATEGORY_NAME = ".catName_SDxtJ"

    # ========== 右侧商品列表 ==========
    GOODS_SCROLL = ".goodsScroll_jgo_K"
    GOOD_SECTION = ".catSection_Ndz_F"
    GOOD_ITEM = ".goodsItem_lrDXM"
    GOOD_NAME = ".goodsName_ahwBK"
    GOOD_ADD_BTN = ".addBtn_We3Mw"
    GOOD_QTY_CONTROL = ".qtyControl_qJ3wn"
    GOOD_QTY_BTN = ".qtyBtn_gNy0_"
    GOOD_QTY_NUM = ".qtyNum_f9OQY"
    EMPTY_TIP = ".emptyTip_x9z8u"

    # ========== 地址选择弹层（AddressPicker） ==========
    ADDRESS_POPUP = ".nut-popup"
    ADDRESS_POPUP_CLOSE = ".closeBtn_fOHrM"
    ADDRESS_CARD = ".card_gJD5h"
    EMPTY_TITLE = ".emptyTitle_TmwiI"
    CREATE_BTN = ".createBtn_a5lOc"

    # ========== 悬浮购物车（MiniCart） ==========
    MINI_CART = ".miniCart_MLTJZ"
    CART_ICON = ".cartIconWrap_E6l2Q"
    CART_BADGE = ".badge_XfXPI"
    CART_MASK = ".maskOverlay_xP6yR"
    CART_LIST = ".list_J8hYA"
    CART_ROW = ".row_CrajV"
    CART_ROW_CONTENT = ".rowContent_mnLYh"
    CART_QTY_BTN = ".qtyBtn_OQBCM"
    CART_QTY_NUM = ".qtyNum_OKTkj"
    CART_PRICE = ".price_s4FlV"
    CART_NAME = ".name_LSLdQ"
    CART_CLEAR_BTN = ".clearBtn_KKnbE"
    CART_TOTAL_AMOUNT = ".totalAmount_zFzJo"
    CART_CHECKOUT_BTN = ".checkout_WLsP0"
    CART_CHECKOUT_BTN_DISABLED = ".checkout_WLsP0.disabled_X_4rl"
    CART_QTY_COUNT = ".count_waRqR"
    # NutUI Dialog（清空购物车二次确认）
    DIALOG_OK_BTN = ".nut-dialog__footer-ok"

    def __init__(self, mini: Any) -> None:
        super().__init__(mini)

    # ================= 页面跳转 =================

    @allure.step("打开外卖页")
    def open(self) -> "TakeoutPage":
        """跳转到外卖页（已在该页则跳过）"""
        if not self.is_at_takeout_page():
            self.switch_tab(self.PATH)
        return self

    @allure.step("返回上一页")
    def to_back(self) -> "TakeoutPage":
        """返回上一页"""
        self.go_back()
        return self

    # ================= 页面断言 =================

    def is_at_takeout_page(self) -> bool:
        return "takeout" in self.get_page_path()

    def is_at_confirm_order_page(self) -> bool:
        """是否已跳转到确认订单页（提交订单入口）"""
        return "confirmOrder" in self.get_page_path()

    def is_show_takeout_title(self) -> bool:
        """是否显示外卖标题"""
        return self.get_text(self.TOP_TITLE) == "外送"

    def is_show_address_placeholder(self) -> bool:
        """是否显示未选地址占位文本"""
        return self.get_text(self.ADDRESS_TEXT) == "请选择地址"

    def get_address_text(self) -> str:
        """获取顶部地址栏文本"""
        return self.get_text(self.ADDRESS_TEXT)

    def get_store_name(self) -> str:
        """获取配送门店名称"""
        return self.get_text(self.STORE_NAME)

    def is_exist_category_active(self) -> bool:
        """是否存在选中态分类元素"""
        return self.is_exists(self.CATEGORY_ACTIVE)

    def is_show_empty_tip(self) -> bool:
        """是否显示「暂无商品」空态"""
        return self.is_exists(self.EMPTY_TIP)

    # ================= 分类切换 =================

    def get_category_names(self) -> List[str]:
        """获取左侧全部分类名称"""
        elements = self.find_elements(self.CATEGORY_NAME) or []
        return [e.inner_text for e in elements]

    def get_active_category_name(self) -> str:
        """获取当前高亮分类名称"""
        return self.get_text(self.CATEGORY_ACTIVE)

    @allure.step("切换分类: 第{index}个")
    def switch_category_by_index(self, index: int) -> "TakeoutPage":
        """点击左侧第 index 个分类（0 基）"""
        items = self.find_elements(self.CATEGORY_ITEM) or []
        if index < len(items):
            items[index].tap()
            time.sleep(1)
        else:
            logger.warning(f"分类下标越界: {index}/{len(items)}")
        return self

    @allure.step("切换分类: {name}")
    def switch_category_by_name(self, name: str) -> "TakeoutPage":
        """按名称点击左侧分类"""
        self.tap(self.CATEGORY_ITEM, inner_text=name)
        time.sleep(1)
        return self

    # ================= 商品列表滑动 / banner 滑动 =================

    @allure.step("商品列表滑动到: y={y}")
    def scroll_goods_list(self, y: int = 600) -> "TakeoutPage":
        """右侧商品列表上下滑动（y>0 向下滚动到指定位置，y=0 回顶）"""
        scroll_view = self.find_element(self.GOODS_SCROLL)
        if scroll_view:
            scroll_view.scroll_to(0, y)
            time.sleep(1)
        return self

    @allure.step("商品列表回到顶部")
    def scroll_goods_list_to_top(self) -> "TakeoutPage":
        """右侧商品列表回顶"""
        return self.scroll_goods_list(0)

    def get_goods_scroll_top(self) -> int:
        """获取商品列表当前滚动位置"""
        scroll_view = self.find_element(self.GOODS_SCROLL)
        if not scroll_view:
            return 0
        value = scroll_view.scroll_top
        # minium call_func 返回 DevToolMessage(dict)，实际数值在 result 字段中
        if isinstance(value, dict):
            value = value.get("result", 0)
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            logger.warning(f"scroll_top 返回值异常: {value!r}")
            return 0

    def is_show_banner(self) -> bool:
        """banner 轮播位是否渲染（未配置轮播类目时不渲染）"""
        return self.is_exists(self.BANNER)

    @allure.step("banner滑动到第{index}张")
    def swipe_banner_to(self, index: int) -> "TakeoutPage":
        """banner 左右滑动到指定下标（0 基）"""
        swiper = self.find_element(self.BANNER_SWIPER)
        if swiper:
            swiper.swipe_to(index)
            time.sleep(1)
        return self

    def get_banner_current(self) -> int:
        """获取 banner 当前展示的下标"""
        current = self.get_attribute(self.BANNER_SWIPER, attribute="current")
        try:
            return int(current)
        except (TypeError, ValueError):
            return 0

    # ================= 地址选择 / 添加地址 =================

    @allure.step("打开地址选择弹层")
    def open_address_popup(self) -> "TakeoutPage":
        """点击顶部地址栏，打开地址选择弹层"""
        self.tap(self.ADDRESS_MAIN)
        time.sleep(1)
        return self

    def is_address_popup_visible(self) -> bool:
        """地址选择弹层是否可见"""
        return self.is_visible(self.ADDRESS_POPUP)

    def is_show_empty_address(self) -> bool:
        """是否显示「暂无收货地址」空态"""
        return self.is_exists(self.EMPTY_TITLE)

    def get_address_card_count(self) -> int:
        """获取弹层内地址卡片数量"""
        cards = self.find_elements(self.ADDRESS_CARD) or []
        return len(cards)

    def get_address_card_texts(self) -> List[str]:
        """获取弹层内全部地址卡片的文本（用于匹配当前选中地址）"""
        cards = self.find_elements(self.ADDRESS_CARD) or []
        return [card.inner_text for card in cards]

    @allure.step("选择第{index}个地址")
    def select_address(self, index: int = 0) -> "TakeoutPage":
        """点击弹层内第 index 个地址卡片（0 基），选中后弹层自动关闭"""
        cards = self.find_elements(self.ADDRESS_CARD) or []
        if index < len(cards):
            cards[index].tap()
            time.sleep(2)  # 选中后触发门店匹配 + 商品刷新
        else:
            logger.warning(f"地址下标越界: {index}/{len(cards)}")
        return self

    @allure.step("关闭地址选择弹层")
    def close_address_popup(self) -> "TakeoutPage":
        """点击右上角 × 关闭地址弹层"""
        self.tap(self.ADDRESS_POPUP_CLOSE)
        time.sleep(0.5)
        return self

    @allure.step("点击新建收货地址")
    def tap_create_address(self) -> "TakeoutPage":
        """点击弹层底部「新建收货地址」，跳转地址详情页（需已登录）"""
        self.tap(self.CREATE_BTN)
        time.sleep(2)
        return self

    # ================= 列表加购 / 查看商品详情 =================

    def get_goods_count(self) -> int:
        """获取当前可见商品数量"""
        items = self.find_elements(self.GOOD_ITEM) or []
        return len(items)

    def get_goods_name(self, index: int = 0) -> str:
        """获取第 index 个商品名称"""
        names = self.find_elements(self.GOOD_NAME) or []
        if index < len(names):
            return names[index].inner_text
        return ""

    @allure.step("列表加购第{index}个商品")
    def add_goods_to_cart_from_list(self, index: int = 0) -> "TakeoutPage":
        """点击第 index 个商品的加购按钮（需已登录且已选地址）"""
        items = self.find_elements(self.GOOD_ITEM) or []
        if index >= len(items):
            logger.warning(f"商品下标越界: {index}/{len(items)}")
            return self
        item = items[index]
        try:
            add_btn = item.get_element(self.GOOD_ADD_BTN, max_timeout=2)
            add_btn.tap()
        except Exception:
            # 已有数量时展示 +/- 控件，点击「+」按钮（第 2 个 qtyBtn）
            try:
                qty_btns = item.get_elements(self.GOOD_QTY_BTN, max_timeout=2)
                if qty_btns and len(qty_btns) >= 2:
                    qty_btns[1].tap()
            except Exception as e:
                logger.error(f"列表加购失败: {e}")
        time.sleep(1)
        return self

    @allure.step("列表减购第{index}个商品")
    def minus_goods_from_list(self, index: int = 0) -> "TakeoutPage":
        """点击第 index 个商品的「-」按钮"""
        items = self.find_elements(self.GOOD_ITEM) or []
        if index >= len(items):
            return self
        try:
            qty_btns = items[index].get_elements(self.GOOD_QTY_BTN, max_timeout=2)
            if qty_btns:
                qty_btns[0].tap()
                time.sleep(1)
        except Exception as e:
            logger.error(f"列表减购失败: {e}")
        return self

    def get_goods_qty_in_list(self, index: int = 0) -> int:
        """获取第 index 个商品在列表上展示的已购数量（无控件返回 0）"""
        items = self.find_elements(self.GOOD_ITEM) or []
        if index >= len(items):
            return 0
        try:
            qty = items[index].get_element(self.GOOD_QTY_NUM, max_timeout=2)
            return int(qty.inner_text)
        except Exception:
            return 0

    @allure.step("从列表打开第{index}个商品详情")
    def open_goods_detail_from_list(self, index: int = 0) -> GoodsDetailPage:
        """点击第 index 个商品卡片，跳转商品详情页"""
        items = self.find_elements(self.GOOD_ITEM) or []
        if index < len(items):
            items[index].tap()
            time.sleep(2)
        else:
            logger.warning(f"商品下标越界: {index}/{len(items)}")
        return GoodsDetailPage(self.mini)

    # ================= 购物车 =================

    def is_cart_visible(self) -> bool:
        """悬浮购物车是否显示（购物车有商品时才显示）"""
        return self.is_exists(self.MINI_CART)

    def is_cart_expanded(self) -> bool:
        """购物车弹窗是否处于展开态"""
        return self.is_exists(self.CART_LIST)

    @allure.step("查看购物车（展开弹窗）")
    def open_cart(self) -> "TakeoutPage":
        """点击购物车图标展开购物车弹窗"""
        if not self.is_cart_expanded():
            self.tap(self.CART_ICON)
            time.sleep(1)
        return self

    @allure.step("关闭购物车弹窗")
    def close_cart(self) -> "TakeoutPage":
        """点击遮罩关闭购物车弹窗"""
        if self.is_cart_expanded():
            self.tap(self.CART_MASK)
            time.sleep(1)
        return self

    def get_cart_badge_count(self) -> int:
        """获取购物车角标数量"""
        text = self.get_text(self.CART_BADGE)
        try:
            return int(text)
        except (TypeError, ValueError):
            return 0

    def get_cart_row_items(self):
        """获取购物车弹窗内每一行的数量与单价（需先展开购物车）
        """
        rows = self.find_elements(self.CART_ROW) or []
        items = []
        for idx, row in enumerate(rows):
            name = ''
            qty = 0
            price = 0.0
            try:
                qty_el = row.get_element(self.CART_QTY_NUM, max_timeout=2)
                qty = int(qty_el.inner_text)
            except Exception as e:
                logger.warning(f"购物车第 {idx} 行数量读取失败: {e}")
            try:
                price_el = row.get_element(self.CART_PRICE, max_timeout=2)
                price = self._parse_money(price_el.inner_text)
            except Exception as e:
                logger.warning(f"购物车第 {idx} 行单价读取失败: {e}")
            try:
                name_el = row.get_element(self.CART_NAME, max_timeout=2)
                name = name_el.inner_text
            except Exception as e:
                logger.warning(f"购物车第 {idx} 行单价读取失败: {e}")
            items.append({"name": name, "qty": qty, "price": price})
        return items

    def calc_cart_amount(self) -> float:
        """通过累加每行「单价 × 数量」计算购物车总金额"""
        return round(sum(it["qty"] * it["price"] for it in self.get_cart_row_items()), 2)

    def calc_cart_total_qty(self) -> int:
        """通过累加每行数量计算购物车总数量"""
        return sum(it["qty"] for it in self.get_cart_row_items())

    @staticmethod
    def _parse_money(text: str) -> float:
        """解析金额文本（去除 ¥/¥ 等货币符号）"""
        if text is None:
            return 0.0
        cleaned = str(text).replace("¥", "").replace("￥", "").replace(",", "").strip()
        if not cleaned:
            return 0.0
        try:
            return float(cleaned)
        except (TypeError, ValueError):
            logger.warning(f"金额解析失败: {text!r}")
            return 0.0

    def get_cart_total_amount(self):
        """获取购物车合计金额文本"""
        total_amount = self.get_text(self.CART_TOTAL_AMOUNT)
        return self._parse_money(total_amount)

    def get_cart_total_qty(self):
        """获取购物车合计数量文本"""
        total_qty = self.get_text(self.CART_QTY_COUNT)
        return int(total_qty)

    @allure.step("购物车内修改第{index}行数量: {delta}")
    def change_cart_qty(self, index: int = 0, delta: int = 1) -> "TakeoutPage":
        """购物车弹窗内点击 -/+ 修改数量（delta>0 点+，否则点-）"""
        rows = self.find_elements(self.CART_ROW) or []
        if index >= len(rows):
            return self
        try:
            btns = rows[index].get_elements(self.CART_QTY_BTN, max_timeout=2)
            if btns and len(btns) >= 2:
                (btns[1] if delta > 0 else btns[0]).tap()
                time.sleep(1)
        except Exception as e:
            logger.error(f"购物车改数量失败: {e}")
        return self

    @allure.step("从购物车打开第{index}行商品详情")
    def open_goods_detail_from_cart(self, index: int = 0) -> GoodsDetailPage:
        """点击购物车弹窗内第 index 行商品，跳转商品详情页"""
        rows = self.find_elements(self.CART_ROW) or []
        if index < len(rows):
            try:
                rows[index].get_element(self.CART_ROW_CONTENT, max_timeout=2).tap()
                time.sleep(2)
            except Exception as e:
                logger.error(f"点击购物车商品失败: {e}")
        return GoodsDetailPage(self.mini)

    @allure.step("清空购物车")
    def clear_cart(self) -> "TakeoutPage":
        """点击「清空」并在二次确认弹窗中点「确认」"""
        self.open_cart()
        self.tap(self.CART_CLEAR_BTN)
        time.sleep(1)
        # NutUI Dialog 确认按钮，找不到时按文案兜底
        if self.is_exists(self.DIALOG_OK_BTN):
            self.tap(self.DIALOG_OK_BTN)
        else:
            self.tap("view", inner_text="确认")
        time.sleep(1)
        return self

    @allure.step("提交订单（点击选好了）")
    def checkout(self) -> "TakeoutPage":
        """点击购物车「选好了」按钮，跳转确认订单页"""
        self.tap(self.CART_CHECKOUT_BTN)
        time.sleep(2)
        return self
