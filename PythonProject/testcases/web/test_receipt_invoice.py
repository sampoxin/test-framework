"""后台管理系统 - 收票列表页测试"""
import random

import allure
import pytest

from utils.logger import logger
from web.pages.receipt_invoice_page import ReceiptInvoicePage
from web.utils.assert_helper import AssertHelper
from web.components.sidebar import Sidebar


@allure.story("收票列表功能")
class TestReceiptInvoice:
    """收票页面测试"""

    @pytest.mark.order(1)
    def test_01_go_to_invoice_page(self, admin_page):
        """左侧导航栏进入收票页面"""
        sidebar = Sidebar(admin_page)
        sidebar.expand_and_click("三单匹配", "收票列表")
        admin_page.wait_for_load_state("networkidle")
        assert sidebar.is_menu_active("收票列表"), "收票列表菜单未激活"

    @pytest.mark.order(2)
    def test_02_next_page(self, admin_page):
        """翻页 - 下一页"""
        page = ReceiptInvoicePage(admin_page)
        total_pages = len(page.get_total_pages())
        current_idx = int(page.get_active_page())
        if total_pages < 2:
            pytest.skip("总页数不足 2 页，跳过")
        page.next_page()
        next_idx = int(page.get_active_page())
        assert next_idx == current_idx + 1, f"下一页应为 {current_idx + 1}，实际 {next_idx}"

    @pytest.mark.order(3)
    def test_03_prev_page(self, admin_page):
        """翻页 - 上一页"""
        page = ReceiptInvoicePage(admin_page)
        current_idx = int(page.get_active_page())
        if current_idx <= 1:
            pytest.skip("已在第一页，无法上一页")
        page.prev_page()
        prev_idx = int(page.get_active_page())
        assert prev_idx == current_idx - 1, f"上一页应为 {current_idx - 1}，实际 {prev_idx}"

    @pytest.mark.order(4)
    def test_04_choose_page(self, admin_page):
        """翻页 - 选择页码跳转"""
        logger.info("选择页码跳转")
        page = ReceiptInvoicePage(admin_page)
        current_idx = int(page.get_active_page())
        pages = page.get_total_pages()
        # 排除当前页，随机选一个
        if len(pages) < 2:
            pytest.skip("总页数不足 2 页，无法选择")
        else:
            available = pages[current_idx:] + pages[:current_idx-1]
            random.choice(available).click()
            page.wait_for_load()
            new_idx = int(page.get_active_page())
            assert new_idx != current_idx, "选择页码后应跳转到不同页"

    @pytest.mark.order(5)
    def test_05_input_page(self, admin_page):
        """翻页 - 输入页码跳转"""
        page = ReceiptInvoicePage(admin_page)
        current_idx = int(page.get_active_page())
        pages = page.get_total_pages()
        total = int(pages[-1].text_content())
        if total <= 1:
            pytest.skip("总页数不足 2 页，无法输入跳转")
        # 随机选一个不同于当前页的页码
        target = current_idx
        while target == current_idx:
            target = random.randint(1, total)
        page.input_page(str(target))
        new_idx = int(page.get_active_page())
        assert new_idx == target, f"输入页码 {target}，实际跳转到 {new_idx}"

    @pytest.mark.order(6)
    def test_06_change_page_size(self, admin_page):
        """切换每页条数"""
        page = ReceiptInvoicePage(admin_page)
        page.change_page_size(20)
        items_after = page.get_total_items()
        assert items_after > 0, "切换后表格应有数据"
        assert items_after <= 20, f"每页 20 条，实际 {items_after} 条"

    @pytest.mark.order(7)
    def test_07_search_and_reset(self, admin_page):
        """搜索 + 重置"""
        page = ReceiptInvoicePage(admin_page)
        # 执行组合查询
        page.search(
            销方名称="达维",
            发票状态="正常",
            开票时间=("2026-07-01", "2026-07-20"),
        )

        # 断言：搜索条件已填入
        assert page.get_search_value("销方名称") == "达维", "销方名称未正确填入"

        # 断言：结果中销方名称都包含"达维"
        seller_names = page.get_column_values("销方名称")
        for name in seller_names:
            assert "达维" in name, f"搜索结果包含不匹配记录: {name}"

        # 重置并验证
        page.reset_search()
        assert page.get_search_value("销方名称") == "", "重置后销方名称应清空"

    @pytest.mark.order(8)
    def test_08_view_detail(self, admin_page):
        """查看收票详情"""
        page = ReceiptInvoicePage(admin_page)
        assert_helper = AssertHelper(admin_page)

        if page.get_total_items() == 0:
            pytest.skip("当前页无数据，无法查看详情")

        invoice_no = page.get_first_invoice_no()
        page.view_detail()
        # 等待详情页加载完成（URL 变化或特定元素出现）
        admin_page.wait_for_load_state("networkidle")

        # 断言1：URL 包含发票号码（详情页路由通常含 id）
        assert_helper.assert_url_contains(invoice_no)
        # 断言2：页面 body 文本包含发票号码
        assert_helper.assert_text_contains("body", invoice_no, by="css")

    @pytest.mark.order(9)
    def test_09_view_operation_tab(self, admin_page):
        """详情页 - 切换到操作记录 Tab"""
        page = ReceiptInvoicePage(admin_page)
        page.view_operation()
        admin_page.wait_for_load_state("networkidle")
        active_tab = page.get_operation_active_tab()
        assert "操作记录" in active_tab, f"操作记录 Tab 未激活，当前: {active_tab}"

    @pytest.mark.order(10)
    def test_10_detail_go_back(self, admin_page):
        """从详情返回列表"""
        page = ReceiptInvoicePage(admin_page)
        assert_helper = AssertHelper(admin_page)
        page.detail_go_back()
        admin_page.wait_for_load_state("networkidle")
        assert_helper.assert_text_contains(".ant-page-header-heading-left", "收票管理", by="css")

    @pytest.mark.order(11)
    def test_11_receipt_invoice_operation(self, admin_page):
        """收票操作"""
        page = ReceiptInvoicePage(admin_page)
        page.receipt_invoice_operation(
            收票方式="按发票号码收集",
            发票号码="26432000001683660856"
        )
        # 断言：操作完成后弹窗关闭或出现成功提示
        admin_page.wait_for_load_state("networkidle")
        # 弹窗应已关闭（收票按钮重新可见）
        assert page.is_visible(page.BTN_RECEIPT), "收票操作后弹窗未关闭"
