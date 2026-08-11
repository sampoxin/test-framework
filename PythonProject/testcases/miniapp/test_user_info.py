import pytest
import allure
import time
from testcases.miniapp.base_test import MiniAppBase
from mini.pages.userinfo_page import UserInfoPage
from utils.logger import logger
from utils.tools import nickname


@allure.story("用户信息页")
class TestMiniUserInfo(MiniAppBase):
    """用户信息页功能测试"""
    UID = "1609"

    def setUp(self):
        self.user_info_page = UserInfoPage(self)

    @pytest.mark.order(20)
    @allure.step("进入用户信息页")
    def test_01_view_user_info_page(self):
        """查看用户信息页标题"""
        logger.info("查看用户信息页标题")
        self.user_info_page.open()
        self.user_info_page.wait_for_user_info()
        assert self.user_info_page.get_field_value("UID") == self.UID, "用户ID不对"
        assert self.user_info_page.is_at_user_info_page(), "应在用户信息页页面"

    @pytest.mark.order(21)
    @allure.step("修改性别")
    def test_02_modify_gender(self):
        """修改性别"""
        logger.info("修改性别")
        new_gender = self.user_info_page.modify_gender()
        logger.info(f"修改性别为:{new_gender}")
        if new_gender is None:
            assert False, "修改性别失败"
        elif new_gender == 0:
            assert self.user_info_page.get_gender() == '男', "修改性别失败"
        else:
            assert self.user_info_page.get_gender() == '女', "修改性别失败"

    @pytest.mark.order(22)
    @allure.step("修改昵称")
    def test_03_modify_nickname(self):
        """修改昵称"""
        logger.info("修改昵称")
        new_name = nickname()
        result = self.user_info_page.modify_nickname(new_name)
        logger.info(f"修改昵称结果: {result}")
        assert result == new_name, f"昵称修改失败，期望: {new_name}，实际: {result}"

    @pytest.mark.order(23)
    @allure.step("修改生日")
    def test_04_modify_birthday(self):
        """修改生日（每年仅支持修改一次）"""
        logger.info("修改生日")
        old_birthday = self.user_info_page.get_field_value("生日")
        logger.info(f"修改前生日: {old_birthday}")

        success = self.user_info_page.modify_birthday(day_steps=1)
        assert success, "修改生日操作失败"

        new_birthday = self.user_info_page.get_field_value("生日")
        logger.info(f"修改后生日: {new_birthday}")
        assert new_birthday != old_birthday, f"生日未变更: {old_birthday}"

    @pytest.mark.order(24)
    @allure.step("点击手机号")
    def test_05_click_phone_field(self):
        """修改手机号（验证跳转到绑定手机页）"""
        logger.info("修改手机号")
        navigated = self.user_info_page.click_phone_field()
        assert navigated, "未跳转到绑定手机页"
        assert self.user_info_page.is_at_bind_phone_page(), "未在绑定手机页"
        # 返回用户信息页，供后续用例使用
        self.user_info_page.to_back()
        self.user_info_page.wait_for_user_info()

    @pytest.mark.order(25)
    @allure.step("点击头像")
    @pytest.mark.skip(reason="头像选择功能未实现")
    def test_06_tap_avatar(self):
        """修改头像（触发微信原生chooseAvatar，验证点击不报错）"""
        logger.info("修改头像")
        self.user_info_page.open()
        self.user_info_page.wait_for_user_info()
        self.user_info_page.tap_avatar()
        time.sleep(1)
        # chooseAvatar 触发微信原生选择对话框，minium 无法自动化选择图片
        assert self.user_info_page.is_at_user_info_page(), "头像操作后页面异常"
