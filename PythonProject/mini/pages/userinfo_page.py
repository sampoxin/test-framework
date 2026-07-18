"""用户信息页 Page Object"""
import minium
import time
from .base_page import BasePage
from utils.logger import logger


class UserInfoPage(BasePage):
    """用户信息页"""
    PATH = "/packages/user/userInfo/index"
    BIND_PHONE_PATH = "/packages/user/bindPhone/index"

    USER_INFO = ".text_kRjqw"
    GENDER_POPUP = ".nut-popup"
    PICKER_LIST = ".nut-pickerview-list"
    CONFIRM_BTN = ".nut-picker-confirm-btn"
    CONFIRM_OK = ".nut-button-primary-children"
    NICK_INPUT = ".nickInput_VR7um"
    EDIT_ICON = ".editIcon_L0kcW"
    AVATAR_BTN = ".avatar-btn_PlGVV"

    def __init__(self, mini: minium.Minium):
        super().__init__(mini)

    def open(self):
        """跳转到用户信息页（已在该页则跳过）"""
        if not self.is_at_user_info_page():
            self.navigate_to(self.PATH)
        return self

    def to_back(self):
        """返回上一页"""
        self.go_back()
        return self

    def is_at_user_info_page(self) -> bool:
        return "userInfo" in self.get_page_path()

    def is_at_bind_phone_page(self) -> bool:
        return "bindPhone" in self.get_page_path()

    def wait_for_user_info(self):
        return self.wait_for_page(self.PATH)

    # ========== 数据获取方法 ==========
    def get_gender(self) -> str:
        elem = self.find_element(self.USER_INFO, inner_text='男')
        return '男' if elem else '女'

    def get_field_value(self, label: str) -> str:
        """获取字段值（性别/手机号/生日等）"""
        elements = self.find_elements(self.USER_INFO)
        if not elements:
            return ""
        for i, elem in enumerate(elements):
            if elem.text == label and i + 1 < len(elements):
                return elements[i + 1].text
        return ""

    def get_nickname(self) -> str:
        inp = self.find_element(self.NICK_INPUT, max_timeout=5)
        if not inp:
            return ""
        val = inp.attribute("value")
        if isinstance(val, list):
            val = val[0] if val else ""
        return val

    # ========== 修改性别 ==========
    def modify_gender(self, target_gender: str = None):
        """修改性别，不传 target_gender 则自动切换"""
        if not self.is_at_user_info_page():
            self.open().wait_for_user_info()

        genders = ['男', '女']
        current_gender = self.get_gender()
        logger.info(f"当前性别: {current_gender}")

        if target_gender is None:
            target_gender = '女' if current_gender == '男' else '男'
        target_idx = genders.index(target_gender)
        current_idx = genders.index(current_gender)

        # 点击性别区域打开选择器
        self.tap(self.USER_INFO, inner_text=current_gender)
        if not self.wait_for_element(self.GENDER_POPUP):
            logger.error("性别选择弹窗未出现")
            return None

        # 需要切换性别
        if target_idx != current_idx:
            picker = self.find_element(self.PICKER_LIST, max_timeout=5)
            self._swipe_picker_column(picker, target_idx - current_idx + 1)

        # 点击确认
        self._tap_confirm()
        logger.info(f"已选择性别: {target_gender}")
        return target_idx

    # ========== 修改昵称 ==========
    def modify_nickname(self, new_name: str) -> str:
        """修改昵称（最长10字符），失焦自动保存"""
        if not self.is_at_user_info_page():
            self.open().wait_for_user_info()

        self.input(self.NICK_INPUT, text = new_name)
        # 点击页面其他区域触发 blur 保存
        self.tap(self.EDIT_ICON)
        time.sleep(0.5)
        return self.get_nickname()

    # ========== 修改生日 ==========
    def modify_birthday(self, day_steps: int = 1) -> bool:
        """修改生日（滑动日期选择器的"日"列）

        Args:
            day_steps: 日列滑动步数，正数=往后选，负数=往前选
        Returns:
            是否操作成功（提交后本年度不能修改）
        """
        if not self.is_at_user_info_page():
            self.open().wait_for_user_info()

        current_birthday = self.get_field_value("生日")
        logger.info(f"当前生日: {current_birthday}")

        # 点击生日行打开 DatePicker
        self.tap(self.USER_INFO, inner_text=current_birthday)
        if not self.wait_for_element(self.GENDER_POPUP):
            logger.error("日期选择器未出现")
            return False

        # DatePicker 有3列: [年, 月, 日]
        pickers = self.find_elements(self.PICKER_LIST, max_timeout=5)
        if not pickers or len(pickers) < 3:
            logger.error(f"日期选择器列数不足: {len(pickers) if pickers else 0}")
            return False

        # 滑动"日"列（第3列，索引2）
        if day_steps != 0:
            self._swipe_picker_column(pickers[2], day_steps)

        # 点击 DatePicker 确认按钮
        self._tap_confirm()

        # 点击确认弹窗的"确定"按钮
        return self._confirm_birthday_change()

    # ========== 修改头像 ==========
    def tap_avatar(self):
        """点击头像区域，触发微信 chooseAvatar 原生选择"""
        self.tap(self.AVATAR_BTN)

    # ========== 修改手机号 ==========
    def click_phone_field(self):
        """点击手机号行，跳转到绑定手机页"""
        if not self.is_at_user_info_page():
            self.open().wait_for_user_info()

        phone = self.get_field_value("手机号")
        logger.info(f"当前手机号: {phone}")
        self.tap(self.USER_INFO, inner_text=phone)
        time.sleep(2)
        return self.is_at_bind_phone_page()

    # ========== 内部方法 ==========
    def _tap_confirm(self, max_retries: int = 3):
        """点击确认按钮，通过重新查找按钮判断弹窗是否已关闭"""
        for attempt in range(max_retries):
            # 每次都重新查找，避免引用已消失的 DOM 元素
            btns = self.find_elements(self.CONFIRM_BTN, max_timeout=0)
            if not btns:
                logger.info(f"弹窗已关闭 (第{attempt + 1}次)")
                return
            btns[0].tap()
            time.sleep(0.8)
        logger.warning(f"点击确认按钮 {max_retries} 次后弹窗仍未关闭")

    def _swipe_picker_column(self, picker_elem, steps: int):
        """滑动单个选择器列
        Args:
            picker_elem: 选择器列元素
            steps: 滑动步数
        """
        y_offset = -steps * 36  # 每步约36px
        logger.info(f"滑动选择器: steps={steps}, offset={y_offset}")
        picker_elem.move(0, y_offset, move_delay=500, smooth=True)

    def _confirm_birthday_change(self) -> bool:
        """确认生日修改（点击确认弹窗）"""
        ok_btn = self.find_element(self.CONFIRM_OK,inner_text="确定",max_timeout=5)
        if ok_btn:
            ok_btn.tap()
            logger.info("已确认生日修改")
            time.sleep(1)
            return True
        logger.warning("未找到确认弹窗确定按钮")
        return False