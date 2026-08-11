"""地址详情页（新建/编辑地址）Page Object

覆盖业务点：添加地址（填写收货人/手机号/详细地址、选择定位、选择标签、设为默认、保存）
"""
import time
from typing import Any, List, Optional

import allure
from .base_page import BasePage
from utils.logger import logger


class AddressDetailPage(BasePage):
    """地址详情页（路由带 id=编辑，不带=新增）"""
    PATH = "/packages/user/address/detail/index"

    BACK_BTN = ".nut-navbar-left"

    # ========== 表单元素 ==========
    PAGE = ".page_E2iBq"
    FIELD = ".field_IrDCO"
    LABEL = ".label_Ag45K"
    INPUT = ".input_w1_Tz"           # 收货人/手机号/详细地址输入框 + 收货地址展示文本共用
    LOCATION_PLACEHOLDER = ".placeholder_b4S2H"
    TAG = ".tag_DfZQI"
    TAG_ACTIVE = ".tagActive_RaIAZ"
    SWITCH_ROW = ".switchRow_xI5e6"
    SUBMIT_BTN = ".submitBtn_fI_J4"

    # input 组件顺序（页面上共 3 个 input：收货人/手机号/详细地址）
    INPUT_IDX_RECEIVER = 0
    INPUT_IDX_PHONE = 1
    INPUT_IDX_DETAIL = 2

    def __init__(self, mini: Any) -> None:
        super().__init__(mini)

    # ================= 页面跳转 =================

    @allure.step("打开地址详情页")
    def open(self, address_id: Optional[str] = None) -> "AddressDetailPage":
        """跳转到地址详情页（address_id 有值=编辑，无=新增）"""
        url = f"{self.PATH}?id={address_id}" if address_id else self.PATH
        if not self.is_at_address_detail_page():
            self.navigate_to(url)
        return self

    @allure.step("返回上一页")
    def to_back(self) -> "AddressDetailPage":
        """点击导航栏返回按钮"""
        self.click_back()
        return self

    def click_back(self) -> None:
        """兼容自定义导航栏返回：优先点返回按钮，失败则调用 navigateBack"""
        if self.is_exists(self.BACK_BTN):
            self.tap(self.BACK_BTN)
        else:
            self.go_back()

    def is_at_address_detail_page(self) -> bool:
        return "address/detail" in self.get_page_path()

    # ================= 表单输入 =================

    def _get_inputs(self) -> List[Any]:
        """获取页面全部 input 输入框（0=收货人 1=手机号 2=详细地址）"""
        return self.find_elements("input") or []

    def _input_by_index(self, index: int, text: str) -> None:
        inputs = self._get_inputs()
        if index < len(inputs):
            inputs[index].input(text)
        else:
            logger.warning(f"输入框下标越界: {index}/{len(inputs)}")

    @allure.step("输入收货人: {name}")
    def input_receiver_name(self, name: str) -> "AddressDetailPage":
        """输入收货人姓名"""
        self._input_by_index(self.INPUT_IDX_RECEIVER, name)
        return self

    @allure.step("输入手机号: {phone}")
    def input_phone(self, phone: str) -> "AddressDetailPage":
        """输入手机号"""
        self._input_by_index(self.INPUT_IDX_PHONE, phone)
        return self

    @allure.step("输入详细地址: {detail}")
    def input_detail_address(self, detail: str) -> "AddressDetailPage":
        """输入详细地址（楼栋/门牌号等）"""
        self._input_by_index(self.INPUT_IDX_DETAIL, detail)
        return self

    @allure.step("点击收货地址定位选择")
    def tap_location_field(self) -> "AddressDetailPage":
        """点击「收货地址」行，唤起微信原生地图选点（原生弹窗需借助 app.handle_modal 等处理）"""
        self.tap(self.FIELD, inner_text="收货地址")
        time.sleep(1)
        return self

    def get_location_text(self) -> str:
        """获取收货地址定位展示文本（未选择时为「点击选择地址定位」）"""
        fields = self.find_elements(self.FIELD) or []
        # 收货地址为第 3 个 field（0=收货人 1=手机号 2=收货地址）
        if len(fields) >= 3:
            try:
                return fields[2].get_element(self.INPUT, max_timeout=2).inner_text
            except Exception:
                return ""
        return ""

    def is_location_selected(self) -> bool:
        """是否已选择定位"""
        text = self.get_location_text()
        return bool(text) and text != "点击选择地址定位"

    # ================= 地址标签 / 默认开关 =================

    @allure.step("选择地址标签: {tag_name}")
    def select_tag(self, tag_name: str) -> "AddressDetailPage":
        """点击地址标签（家/公司/学校/其他），再次点击可取消"""
        self.tap(self.TAG, inner_text=tag_name)
        return self

    def get_active_tag(self) -> str:
        """获取当前选中的标签文本（未选中返回空串）"""
        return self.get_text(self.TAG_ACTIVE)

    @allure.step("切换设为默认地址开关")
    def toggle_default_switch(self) -> "AddressDetailPage":
        """点击「设为默认地址」开关"""
        switch = self.find_element("switch")
        if switch:
            switch.tap()
        return self

    def is_default_checked(self) -> bool:
        """默认地址开关是否已打开"""
        checked = self.get_attribute("switch", attribute="checked")
        return str(checked).lower() == "true"

    # ================= 保存提交 =================

    def get_submit_btn_text(self) -> str:
        """获取提交按钮文案（保存/保存中...）"""
        return self.get_text(self.SUBMIT_BTN)

    @allure.step("点击保存")
    def save(self) -> "AddressDetailPage":
        """点击保存按钮（保存成功后约 1s 自动返回上一页）"""
        self.tap(self.SUBMIT_BTN)
        time.sleep(2)
        return self

    def is_save_success(self, timeout: int = 5) -> bool:
        """保存成功后页面会自动 navigateBack，以离开本页作为成功依据"""
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_at_address_detail_page():
                return True
            time.sleep(0.5)
        return False

    @allure.step("填写并保存地址")
    def fill_and_save(
        self,
        receiver_name: str,
        phone: str,
        detail_address: str,
        tag_name: Optional[str] = None,
        is_default: bool = False,
    ) -> "AddressDetailPage":
        """一站式填写地址表单并保存

        注意：保存前必须已选择定位（经纬度），否则会 toast「请选择收货地址」；
        原生地图选点无法通过 DOM 操作完成，需在用例层配合 tap_location_field 处理。
        """
        self.input_receiver_name(receiver_name)
        self.input_phone(phone)
        self.input_detail_address(detail_address)
        if tag_name:
            self.select_tag(tag_name)
        if is_default and not self.is_default_checked():
            self.toggle_default_switch()
        return self.save()
