"""
三单匹配-批量推送结算单（混合匹配）

发票分两路处理：
  - 人工匹配 → 编辑商品代码 + batch_manual_match + batch_approve
  - 强制匹配 → 生成发票 + approve 审批通过
最终合流：batch_push_settlement 批量推送结算单
"""
import allure
import pytest

from utils.assemble_data import convert_receipt_data, get_item_code, adjust_receipt_amounts


@allure.epic("三单匹配")
@allure.feature("批量推送结算")
class TestBatchSettlement:
    DATA_KEY = "data_6"

    @allure.story("批量收票")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_batch_collect(self, match_api, fixed_data):
        """收取全部 12 张发票"""
        data_6 = fixed_data["data_6"]
        self.__class__.manual_invoices = set(data_6["manual_invoices"])
        self.__class__.force_invoices = set(data_6["force_invoices"])
        self.__class__.invoice_order_map = data_6["invoice_order_map"]

        with allure.step(f"批量收取 {len(self.invoice_nos)} 张发票"):
            for invoice_no in self.invoice_nos:
                match_api.collect_invoice(invoice_no)

    @allure.story("核票查询与分流")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_query_and_split(self, match_api, context):
        """查询全部核票，按人工/强制分流到 context"""
        result = match_api.page_matches(supplierName=self.supplier_name, page_size=50)
        assert result["data"]["total"] > 0, "查询核票失败，未查询到相关数据"

        manual_data = []
        force_data = []
        audit_data = []

        for item in result["data"]["records"]:
            if item["invoiceNo"] not in self.invoice_nos:
                continue

            record = {
                "match_id": item["id"],
                "invoice_no": item["invoiceNo"],
                "invoice_id": item["invoiceId"],
                "invoice_type": item["invoiceType"],
                "supplier_id": item["supplierId"],
            }
            # 过滤待审核状态的核票
            if item["auditStatus"] == 1:
                audit_data.append(item["invoiceId"])

            if item["invoiceNo"] in self.manual_invoices:
                manual_data.append(record)
            else:
                force_data.append(record)

        context["manual_data"] = manual_data
        context["force_data"] = force_data
        context["all_data"] = manual_data + force_data
        context["audit_data"] = audit_data

        assert len(manual_data) == len(self.manual_invoices), \
            f"人工匹配发票数不匹配: 期望 {len(self.manual_invoices)}, 实际 {len(manual_data)}"
        assert len(force_data) == len(self.force_invoices), \
            f"强制匹配发票数不匹配: 期望 {len(self.force_invoices)}, 实际 {len(force_data)}"

    @allure.story("批量审核")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_batch_audit(self, match_api, context):
        """12 张发票统一批量审核"""
        invoice_ids = context.get("audit_data", [])
        if not invoice_ids:
            pytest.skip("无待审核发票ID")
        result = match_api.batch_audit(invoice_ids)
        assert result["data"]["failCount"] == 0, "批量审核失败,存在审核失败的发票"


    @allure.story("强制匹配")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_force_match(self, match_api, context):
        """3 张发票走强制匹配：查询未结算单 → 生成发票 → 审批通过"""
        force_data = context.get("force_data", [])
        if not force_data:
            pytest.skip("无强制匹配发票")

        order_map = self.invoice_order_map
        order_nos = set()
        return_nos = set()
        for item in force_data:
            invoice_no = item["invoice_no"]
            order_no = order_map.get(invoice_no)
            assert order_no, f"发票 {invoice_no} 未找到对应的单据号"
            if order_no.startswith("PO"):
                order_nos.add(order_no)
            else:
                return_nos.add(order_no)
        order_nos = list(order_nos)
        return_nos = list(return_nos)

        # ========== 步骤1：搜索供应商 ==========
        with allure.step("步骤1：搜索供应商"):
            result = match_api.get_supplier_options(keyword=self.supplier_name, limit=20)
            assert result["data"][0]["supplierName"] == self.supplier_name, "未找到供应商"
            supplier_id = result["data"][0]["supplierId"]

        # ========== 步骤2：查询未结算收/退货单 ==========
        with allure.step("步骤2：查询未结算退货单"):
            result = match_api.page_unsettled(
                supplier_id, return_nos=return_nos, order_nos=order_nos
            )
            assert result["data"]["total"] > 0, "查询未结算退货单失败"
            receipts = []
            returns = []
            total_amount_with_tax = 0
            total_amount_with_out_tax = 0
            total_amount_tax = 0
            for item in result["data"]["records"]:
                total_amount_with_tax += item["unmatchedAmountWithTax"]
                total_amount_with_out_tax += item["unmatchedAmountWithoutTax"]
                total_amount_tax += item["unmatchedTaxAmount"]
                if item["docType"] == "RECEIPT":
                    receipts.append(item["receiptOrReturnNo"])
                else:
                    returns.append(item["receiptOrReturnNo"])
            receipt_nos = receipts + returns
            tab_type = "RECEIPT" if total_amount_with_tax>=0 else "RETURN"

        # ========== 步骤3：读取未结算退货单明细 ==========
        with allure.step("步骤3：读取退货单明细"):
            result = match_api.load_receipt_items(
                supplier_id, receipt_nos=receipts, return_nos=returns
            )
            assert len(result["data"]["receiptItems"]) >= len(receipts), "查询未结算收/退货单详情失败,未查询到相关数据"
            receipt_items = convert_receipt_data(result)

        # ========== 步骤4：校验发票信息 ==========
        force_invoice_nos = [item["invoice_no"] for item in force_data]
        with allure.step("步骤4：校验发票信息"):
            result = match_api.check_invoice_summary(supplier_id, force_invoice_nos)
            assert result["data"]["conflictReasons"] == [], \
                f"发票校验冲突: {result['data']['conflictReasons']}"
            invoice_total_amount_with_tax = result['data']['totalAmountWithTax']
            invoice_total_amount_with_out_tax = result['data']['totalAmountWithoutTax']
            invoice_total_amount_tax = result['data']['totalTaxAmount']

        # ========== 步骤5：提交强制匹配生成发票 ==========
        with allure.step(f"步骤5：强制匹配生成 {len(force_invoice_nos)} 张发票"):
            receipt_items = adjust_receipt_amounts(
                receipt_items,
                invoice_total_amount_with_tax,
                invoice_total_amount_with_out_tax,
                invoice_total_amount_tax
            )
            result = match_api.submit_force_match(
                supplier_id, force_invoice_nos, receipt_nos, receipt_items, tab=tab_type
            )
            assert result["data"]["success"] is True, "强制匹配生成发票失败"
            context["force_match_ids"] = result["data"]["matchIds"]

        # ========== 步骤6：逐条审批通过 ==========
        with allure.step(f"步骤6：审批通过 {len(force_data)} 张发票"):
            match_id = force_data[0]["match_id"]
            match_api.approve(
                match_id,
                approved=True,
                supplier_id=supplier_id
            )

    @allure.story("人工匹配")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_manual_match(self, match_api, context):
        """9 张发票走人工匹配：编辑商品代码 → 批量匹配 → 批量审批"""
        manual_data = context.get("manual_data", [])
        if not manual_data:
            pytest.skip("无人工匹配发票")

        # ========== 步骤1：编辑商品代码（每张发票关联对应的单据号） ==========
        order_map = self.invoice_order_map
        with allure.step(f"步骤1：编辑 {len(manual_data)} 张发票的商品代码"):
            for item in manual_data:
                match_id = item["match_id"]
                supplier_id = item["supplier_id"]
                invoice_type = item.get("invoice_type", 2)
                invoice_no = item["invoice_no"]
                # 查找该发票对应的单据号
                order_no = order_map.get(invoice_no)
                assert order_no, f"发票 {invoice_no} 未找到对应的单据号"

                # 查询核票明细
                items_result = match_api.get_invoice_items(match_id, supplier_id)
                assert items_result["data"]["total"] > 0, \
                    f"发票 {invoice_no} 查询核票明细失败"
                invoice_items =[
                    {"id": item["id"], "itemName": item["itemName"], "itemSpec": item["spec"]}
                    for item in items_result["data"]["records"]
                ]
                items = [{"matchItemId": item["id"], "itemCode": get_item_code(item["itemName"], item["itemSpec"])} for
                         item in invoice_items]
                # 按发票类型编辑商品代码，传入对应的单据号
                if invoice_type == 2:
                    # 蓝票(PO收货单)
                    edit_result_json = match_api.edit_item_code( match_id, supplier_id, items, order_nos=[order_no] )
                else:
                    # 红票(RO退货单)
                    edit_result_json = match_api.edit_item_code( match_id, supplier_id, items, return_order_nos=[order_no] )
                assert edit_result_json["data"]["successCount"] == len(items), "编辑商品代码失败,成功记录数不是预期值"

        # ========== 步骤2：批量匹配 ==========
        with allure.step(f"步骤2：批量匹配 {len(manual_data)} 张发票"):
            match_list = [
                {"matchId": item["match_id"], "invoiceId": item["invoice_id"]}
                for item in manual_data
            ]
            result = match_api.batch_manual_match(match_list)
            assert result["data"]["failCount"] == 0, "批量匹配存在失败记录"

        # ========== 步骤3：批量审批通过 ==========
        with allure.step("步骤3：批量审批通过"):
            approval_list = [
                {"matchId": item["match_id"], "approved": True, "remark": "批量推送-人工匹配通过"}
                for item in manual_data
            ]
            result = match_api.batch_approve(approval_list)
            assert result["data"]["failCount"] == 0, "批量审批存在失败记录"



    @allure.story("批量推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_batch_push(self, match_api, context):
        """合流：红蓝票统一批量推送结算"""
        manual_data = context.get("manual_data", [])
        force_data = context.get("force_data", [])
        all_data = manual_data + force_data

        with allure.step("步骤1：按发票类型分组"):
            match_ids = []
            red_match_ids = []
            for item in all_data:
                if item["invoice_type"] == 2:
                    match_ids.append(item["match_id"])
                else:
                    red_match_ids.append(item["match_id"])

        with allure.step(f"步骤2：批量推送（蓝票 {len(match_ids)} 张 + 红票 {len(red_match_ids)} 张）"):
            result = match_api.batch_push_settlement(match_ids, red_match_ids)
            assert result["data"]["failCount"] == 0, "批量推送存在失败记录"

    @allure.story("验证推送结果")
    @pytest.mark.p0
    @pytest.mark.order(7)
    def test_07_verify_push(self, match_api, context, file_helper):
        """逐条验证 12 张发票的推送状态，失败也继续遍历并记录全部结果"""
        all_data = context.get("all_data", [])
        errors = []

        with allure.step(f"验证 {len(all_data)} 张发票推送状态"):
            for item in all_data:
                result = match_api.page_matches(invoiceNo=item["invoice_no"])
                record = result["data"]["records"][0]
                push_status = record.get("pushStatus")
                settle_no = record.get("settleNo", "")
                is_pushed = push_status == 2

                # 无论断言是否通过，都记录到文件
                file_helper.append_json({
                    "matchId": item["match_id"],
                    "invoiceNo": item["invoice_no"],
                    "settleNo": settle_no,
                    "pushStatus": push_status,
                    "isPushed": is_pushed
                }, "test.json")

                if not is_pushed:
                    errors.append(
                        f"发票 {item['invoice_no']} 推送状态不是已推送: pushStatus={push_status}"
                    )

        # 全部遍历完成后再统一断言，确保所有发票都被验证和记录
        assert not errors, "\n".join(errors)