"""后台管理系统 - 收票列表页 Page Object"""
from web.pages.base_page import BasePage
from utils.logger import logger


class ReceiptInvoicePage(BasePage):
    """收票列表页"""

    # ──── 搜索表单 ────
    SEARCH_FORM = ".ant-pro-table-search"
    BTN_SEARCH = 'button:has-text("查 询")'
    BTN_RESET = 'button:has-text("重 置")'

    # ──── 分页 ────
    PAGINATION_ITEM = ".ant-pagination-item"
    PAGINATION_NEXT = ".ant-pagination-next .ant-pagination-item-link"
    PAGINATION_PREV = ".ant-pagination-prev .ant-pagination-item-link"
    PAGINATION_ITEM_ACTIVE = ".ant-pagination-item-active"
    PAGE_BTN = ".ant-pagination-item"
    PAGE_TEXT = 'input[aria-label="页"]'
    PAGE_SIZE_SELECT = "div[aria-label='页码'].ant-select"

    # ──── 表格 ────
    TABLE_ROW = ".ant-table-row"
    TABLE_CELL = "td.ant-table-cell"
    TABLE_HEADER = "th.ant-table-cell"

    # ──── 详情/操作 ────
    BTN_DETAIL_FIRST = ".ant-btn-link:has-text('详情')"
    BTN_OPERATION_TAB = ".ant-tabs-tab"
    BTN_OPERATION_ACTIVE = ".ant-tabs-tab-active"
    BTN_DETAIL_BACK = ".anticon-arrow-left"
    DETAIL_INFO = ".ant-descriptions-item-content"

    # ──── 收票弹窗 ────
    BTN_RECEIPT = 'button:has-text("收 票")'
    RECEIPT_FORM = ".ant-modal-content"
    RECEIPT_METHOD_SELECT = ".ant-select:has(#receiptMethod)"
    RECEIPT_INVOICE_INPUT = f"{RECEIPT_FORM} #invoiceNo"
    BTN_CONFIRM = 'button:has-text("确 定")'
    RECEIPT_SUCCESS_MSG = ".ant-message-success"

    # ──── 字段配置（字段名 → 控件类型映射） ────
    SEARCH_FIELDS = {
        # 输入框（通过 id 精确定位）
        "发票号码": {"type": "input", "selector": "#invoiceNo"},
        "发票代码": {"type": "input", "selector": "#invoiceCode"},
        "数电号码": {"type": "input", "selector": "#elecInvoiceNo"},
        "销方名称": {"type": "input", "selector": "#sellerName"},
        "销方税号": {"type": "input", "selector": "#sellerCode"},
        "购方名称": {"type": "input", "selector": "#buyerName"},
        "购方税号": {"type": "input", "selector": "#buyerCode"},
        # 下拉选择（通过 id 定位 Select 组件）
        "发票类型": {"type": "select", "selector": "#isRedType"},
        "发票状态": {"type": "select", "selector": "#invoiceStatus"},
        # 日期范围（通过 id 定位开始输入框）
        "开票时间": {"type": "date_range", "start_id": "invoiceDate"},
        "收票时间": {"type": "date_range", "start_id": "createTime"},
    }

    # ========================== 搜索操作 ==========================

    def search(self, **kwargs):
        """
        组合查询 - 支持同时设置多个查询条件

        用法示例:
            page.search(发票号码="12345", 发票状态="正常", 开票时间=("2026-07-01", "2026-07-20"))
        """
        for field_name, value in kwargs.items():
            if field_name not in self.SEARCH_FIELDS:
                logger.warning(f"未知查询字段: {field_name}，跳过")
                continue
            config = self.SEARCH_FIELDS[field_name]
            field_type = config["type"]

            if field_type == "input":
                self._fill_input(config["selector"], value)
            elif field_type == "select":
                self._select_option(config["selector"], value)
            elif field_type == "date_range":
                self._pick_date_range(config["start_id"], value[0], value[1])

        self._click_search()
        return self

    def reset_search(self):
        """重置查询条件"""
        logger.info("重置查询条件")
        self.click_element(self.BTN_RESET)
        self.wait_for_load()
        return self

    def _click_search(self):
        """点击查询按钮"""
        logger.info("点击查询")
        self.click_element(self.BTN_SEARCH)
        self.wait_for_load()

    def _fill_input(self, selector: str, value: str):
        """填写输入框"""
        logger.info(f"输入 [{selector}]: {value}")
        self.fill_input(selector, value)

    def _select_option(self, selector: str, option_text: str):
        """
        下拉选择（Ant Design Select）
        1. 通过 id 定位 Select 组件并点击展开
        2. 在可见的下拉面板中点击目标选项
        """
        logger.info(f"下拉选择 [{selector}]: {option_text}")
        self.click_element(selector)
        option = self.find_element(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
            f".ant-select-item-option:has-text('{option_text}')"
        )
        option.click()
        self.page.wait_for_timeout(300)

    def _pick_date_range(self, start_id: str, start_date: str, end_date: str):
        """
        日期范围选择（Ant Design RangePicker）
        1. 通过 id 定位开始日期输入框
        2. 填入开始日期
        3. 在同一 picker 容器内定位结束日期输入框
        4. 填入结束日期并回车确认
        """
        logger.info(f"日期范围 [{start_id}]: {start_date} ~ {end_date}")
        start_input = self.find_element(f"#{start_id}")
        start_input.click()
        start_input.fill(start_date)

        # 同一 .ant-picker 容器内的第二个 input 即结束日期
        picker = start_input.locator("xpath=ancestor::div[contains(@class,'ant-picker')]")
        end_input = picker.locator("input").nth(1)
        end_input.click()
        end_input.fill(end_date)

        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(300)

    # ========================== 翻页功能 ==========================

    def next_page(self):
        """下一页"""
        logger.info("点击下一页")
        self.click_element(self.PAGINATION_NEXT)
        self.wait_for_load()
        return self

    def prev_page(self):
        """上一页"""
        logger.info("点击上一页")
        self.click_element(self.PAGINATION_PREV)
        self.wait_for_load()
        return self

    def choose_page(self, page_number):
        """选择页面跳转"""
        logger.info(f"点击第 {page_number} 页")
        self.click_element(self.PAGINATION_ITEM, page_number)
        self.wait_for_load()
        return self

    def input_page(self, page_number):
        """输入页码"""
        logger.info(f"输入页码: {page_number}")
        self.find_element(self.PAGE_TEXT).fill(page_number)
        # 点击空白区域触发跳转
        self.click_element("body")
        self.wait_for_load()
        return self

    def change_page_size(self, size: int = 20):
        """切换每页条数"""
        logger.info(f"切换每页条数为 {size}")
        self.click_element(self.PAGE_SIZE_SELECT)
        # 在可见下拉面板中选择包含目标数字的选项
        option = self.find_element(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
            f".ant-select-item-option:has-text('{size}')"
        )
        option.click()
        self.wait_for_load()

    # ========================== 详情/操作 ==========================

    def view_detail(self):
        """查看第一行收票详情"""
        logger.info("点击收票详情")
        self.find_element(self.BTN_DETAIL_FIRST).first.click()
        self.wait_for_load()

    def view_operation(self):
        """切换到操作记录 Tab"""
        logger.info("点击操作记录 Tab")
        self.click_element(f"{self.BTN_OPERATION_TAB}:has-text('操作记录')")
        self.wait_for_load()

    def detail_go_back(self):
        """从详情返回列表"""
        logger.info("从详情返回列表")
        self.click_element(self.BTN_DETAIL_BACK)
        self.wait_for_load()

    def receipt_invoice_operation(self, **kwargs):
        """
        收票操作（弹窗表单）

        用法示例:
            page.receipt_invoice_operation(收票方式="按发票号码收集", 发票号码="26432000001683660856",...)
        """
        logger.info(f"收票操作: {kwargs}")
        self.click_element(self.BTN_RECEIPT)
        self.wait_for_selector(self.RECEIPT_FORM)

        for key, value in kwargs.items():
            if key == "收票方式":
                self.click_element(self.RECEIPT_METHOD_SELECT)
                self.find_element(
                    ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                    f".ant-select-item-option:has-text('{value}')"
                ).click()
                self.page.wait_for_timeout(300)

            if key == "发票号码":
                self.fill_input(self.RECEIPT_INVOICE_INPUT, value)

        self.click_element(self.BTN_CONFIRM)
        # 等待操作完成（成功提示或弹窗关闭）
        self.page.wait_for_timeout(1000)

    # ========================== 获取信息 ==========================

    def get_active_page(self) -> str:
        """获取当前激活的页码"""
        return self.get_text_content(self.PAGINATION_ITEM_ACTIVE)

    def get_total_pages(self) -> list:
        """获取总页数按钮列表"""
        return self.find_elements(self.PAGE_BTN)

    def get_total_items(self) -> int:
        """获取当前页表格行数"""
        return len(self.find_elements(self.TABLE_ROW))

    def get_search_value(self, field_name: str) -> str:
        """获取搜索表单字段的当前值"""
        config = self.SEARCH_FIELDS.get(field_name)
        if not config or "selector" not in config:
            return ""
        return self.get_input_value(config["selector"])

    def get_first_invoice_no(self) -> str:
        """获取第一行发票流水号（第2列）"""
        row = self.find_elements(self.TABLE_ROW)[0]
        return row.locator(self.TABLE_CELL).nth(1).inner_text().strip()

    def get_detail_invoice_no(self) -> str:
        """
        获取详情页发票号码
        遍历 ant-descriptions 的 label-value 对，找到"发票号码"对应的值
        """
        labels = self.find_elements(".ant-descriptions-item-label")
        contents = self.find_elements(".ant-descriptions-item-content")
        for label, content in zip(labels, contents):
            label_text = (label.text_content() or "").strip().rstrip("：:")
            if "发票号码" in label_text or "发票代码" in label_text:
                value = (content.text_content() or "").strip()
                if value and value != "-":
                    return value
        # 兜底：返回所有 content 中第一个非 "-" 的值
        for content in contents:
            value = (content.text_content() or "").strip()
            if value and value != "-":
                return value
        return ""

    def get_column_values(self, column_name: str) -> list:
        """
        获取表格某一列的所有文本值
        通过表头文本匹配确定列索引，再提取每行该列的值
        """
        headers = self.page.locator(self.TABLE_HEADER)
        col_index = -1
        for i in range(headers.count()):
            header_text = headers.nth(i).inner_text().strip()
            if column_name in header_text:
                col_index = i
                break
        if col_index == -1:
            logger.warning(f"未找到表头: {column_name}")
            return []

        rows = self.page.locator(self.TABLE_ROW)
        values = []
        for i in range(rows.count()):
            cell = rows.nth(i).locator(self.TABLE_CELL).nth(col_index)
            values.append(cell.inner_text().strip())
        return values

    def get_operation_active_tab(self) -> str:
        """获取详情中当前激活的 Tab 名称"""
        return self.get_text(self.BTN_OPERATION_ACTIVE)

    def is_receipt_success(self) -> bool:
        """收票操作是否成功（成功提示消息可见）"""
        return self.is_visible(self.RECEIPT_SUCCESS_MSG)
