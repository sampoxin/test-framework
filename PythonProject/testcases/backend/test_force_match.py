"""三单匹配-强制匹配正常流程（收票-强制匹配-推送结算单）"""
import allure
import pytest

from utils.assemble_data import convert_receipt_data, adjust_receipt_amounts


@allure.epic("三单匹配")
@allure.feature("强制匹配")
@pytest.mark.parametrize("setup_test_data", ["data_2", "data_5","data_7"], indirect=True)
class TestForceMatch:

    @allure.story("收票/审核")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_invoice_receive(self, match_api, context):
        for item in self.invoice_nos:
            with allure.step("步骤1：收取发票"):
                match_api.collect_invoice(item)

            with allure.step("步骤2：查询发票"):
                result_json = match_api.page_matches(invoiceNo=item)
                assert result_json["data"]["total"] > 0, "查询发票失败,未查询到相关数据"
                invoice_id = result_json["data"]["records"][0]["invoiceId"]
                audit_status = result_json["data"]["records"][0]["auditStatus"]

            with allure.step("步骤3：审核发票"):
                if audit_status != 2:
                    match_api.audit_invoice(invoice_id, audit_status=2)
                else:
                    pytest.skip("发票已审核，无法再次审核")

    @allure.story("查询未结算收/退货单")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_query_unsettled_match(self, match_api, context):
        with allure.step("步骤1：搜索供应商"):
            result_json = match_api.get_supplier_options(limit=20)
            assert len(result_json["data"]) == 20, "查询供应商失败,未查询到相关数据"

        with allure.step("步骤2：搜索指定供应商"):
            result_json = match_api.get_supplier_options(keyword=self.supplier_name, limit=20)
            assert result_json["data"][0]["supplierName"] == self.supplier_name, "查询供应商失败,未查询到相关数据"
            context["supplier_id"] = result_json["data"][0]["supplierId"]

        with allure.step("步骤3：搜索指定供应商的未结算收/退货单"):
            supplier_id = context["supplier_id"]
            result_json = match_api.page_unsettled(
                supplier_id, order_nos=self.receipt_nos, return_nos=self.return_nos
            )
            assert result_json["data"]["total"] > 0, "查询未结算收/退货单失败,未查询到相关数据"
            context["receipt_nos"] = [item["receiptOrReturnNo"] for item in result_json["data"]["records"]]

    @allure.story("生成发票")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_generate_invoice(self, match_api, context):
        supplier_id = context["supplier_id"]
        receipt_nos = context["receipt_nos"]

        with allure.step("步骤1：读取未结算收/退货单详情"):
            result_json = match_api.load_receipt_items(supplier_id, receipt_nos=receipt_nos)
            assert len(result_json["data"]["receiptItems"]) >= len(receipt_nos), "查询未结算收/退货单详情失败,未查询到相关数据"
            receipt_items = convert_receipt_data(result_json)

        with allure.step("步骤2：校验发票信息"):
            result_json = match_api.check_invoice_summary(supplier_id, self.invoice_nos)
            assert result_json["data"]["conflictReasons"] == [], "校验发票信息失败,存在冲突原因"
            invoice_total_amount_with_tax = result_json['data']['totalAmountWithTax']
            invoice_total_amount_with_out_tax = result_json['data']['totalAmountWithoutTax']
            invoice_total_amount_tax = result_json['data']['totalTaxAmount']

        with allure.step("步骤3：生成发票"):
            receipt_items = adjust_receipt_amounts(
                receipt_items,
                invoice_total_amount_with_tax,
                invoice_total_amount_with_out_tax,
                invoice_total_amount_tax
            )
            result_json = match_api.submit_force_match(
                supplier_id, self.invoice_nos, receipt_nos, receipt_items, tab="RECEIPT"
            )
            assert result_json["data"]["success"] == True, "生成发票失败"
            context["match_ids"] = result_json["data"]["matchIds"]

    @allure.story("核票详情")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_invoice_verify(self, match_api, context):
        match_id = context.get("match_ids", [""])[0]
        supplier_id = context.get("supplier_id", "")

        with allure.step("步骤1：查看核票详情"):
            result_json = match_api.get_detail(match_id, supplier_id)
            assert result_json["data"]["invoiceNo"] in self.invoice_nos, "查询核票详情失败,未查询到相关数据,发票号不匹配"
            force_batch_no = result_json["data"]["forceBatchNo"]

        with allure.step("步骤2：查看核票明细"):
            match_api.get_force_result(force_batch_no)

        with allure.step("步骤3：查看费用单抵扣明细"):
            match_api.get_expense_deductions(match_id)

        with allure.step("步骤4：查看预付抵扣明细"):
            match_api.get_pre_settlement_deductions(match_id)

        with allure.step("步骤5：查看核票操作列表"):
            result_json = match_api.page_records(business_id=match_id, supplier_id=supplier_id)
            assert result_json["data"]["total"] > 0, "查询核票操作列表失败,未查询到相关数据"

        with allure.step("步骤6：查看乐檬扣补单明细"):
            match_api.get_make_up_orders(match_id)

    @allure.story("核票通过")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_approval_pass(self, match_api, context):
        match_id = context.get("match_ids", [""])[0]
        supplier_id = context.get("supplier_id", "")
        match_api.approve(match_id, approved=True, supplier_id=supplier_id)

    @allure.story("推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_push_settlement(self, match_api, context, file_helper):
        match_ids = context.get("match_ids", [])
        supplier_id = context.get("supplier_id", "")

        with allure.step("步骤1：查询核票详情-查询推送状态"):
            result_json = match_api.page_matches(matchId=match_ids[0])
            assert result_json["data"]["total"] > 0, "查询核票数据失败,未查询到相关数据"
            assert result_json["data"]["records"][0].get("writeOffStatus") == 2,"核票状态不是已核票"
            push_status =  result_json["data"]["records"][0].get("pushStatus")

        with allure.step("步骤2：查询未结算红票"):
            result_json = match_api.pre_check_settlement(match_ids[0], supplier_id)
            has_pending_red_invoices = result_json["data"].get("hasPendingRedInvoice", False)

        if push_status == 0 or push_status is None:
            with allure.step("步骤3：推送结算单"):
                if not has_pending_red_invoices:
                    match_api.push_settlement(match_ids[0])
                else:
                    file_helper.append_json({"matchId": match_ids,"invoiceNo": self.invoice_nos,"settleNo": "存在未结算红票，需要走红蓝对冲"}, "test.json")
                    pytest.skip("存在未结算红票，需要走红蓝对冲")

        with allure.step("步骤4：查询核票详情-验证推送结果"):
            result_json = match_api.page_matches(matchId=match_ids[0])
            assert result_json["data"]["records"][0].get("pushStatus") == 2, "推送状态不是已推送"
            settle_no = result_json["data"]["records"][0].get("settleNo")
            test_data = {
                "matchId": match_ids,
                "invoiceNo": self.invoice_nos,
                "settleNo": settle_no
            }
            file_helper.append_json(test_data, "test.json")
