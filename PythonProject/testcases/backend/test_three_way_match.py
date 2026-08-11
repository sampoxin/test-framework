"""三单匹配-人工匹配正常流程（收票-核票-匹配-推送结算单）"""
import allure
import pytest
from utils.assemble_data import get_item_code


@allure.epic("三单匹配")
@allure.feature("收票核票")
@pytest.mark.parametrize("setup_test_data", ["data_1","data_8","data_9"], indirect=True)
class TestThreeWayMatch:

    @allure.story("收票")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_invoice_receive(self, match_api, context):
        with allure.step("步骤1：收取发票"):
            match_api.collect_invoice(self.invoice_no)

        with allure.step("步骤2：查询发票"):
            result_json = match_api.page_invoices(invoiceNo=self.invoice_no)
            assert result_json["data"]["total"] > 0, "查询发票失败,未查询到相关数据"
            assert result_json["data"]["records"][0]["invoiceNo"] == self.invoice_no, "查询发票失败,发票号不匹配"
            context["invoice_id"] = result_json["data"]["records"][0]["id"]

        with allure.step("步骤3：查看收票详情"):
            result_json = match_api.get_invoice_detail(context["invoice_id"])
            assert result_json["data"]["invoiceNo"] == self.invoice_no, "查询收票详情失败,发票号不匹配"

        with allure.step("步骤4：查看收票操作列表"):
            result_json = match_api.page_records(
                business_id=context["invoice_id"], business_type=2, page_size=1
            )
            assert result_json["data"]["total"] > 0, "查询收票操作列表失败,未查询到相关数据"

    @allure.story("核票查询")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_invoice_verify_query(self, match_api, context):
        result_json = match_api.page_matches(invoiceNo=self.invoice_no)
        assert result_json["data"]["total"] > 0, "查询核票数据失败,未查询到相关数据"
        record = result_json["data"]["records"][0]
        context["match_id"] = record["id"]
        context["invoice_supplier_id"] = record["supplierId"]
        context["invoice_id"] = record["invoiceId"]
        context["invoice_audit_status"] = record["auditStatus"]
        context["invoice_push_status"] = record["pushStatus"]

    @allure.story("审核发票")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_audit_invoice(self, match_api, context):
        audit_status = context.get("invoice_audit_status", 1)
        if audit_status != 2:
            invoice_id = context.get("invoice_id", "")
            match_api.audit_invoice(invoice_id, audit_status=2)
        else:
            pytest.skip("发票已审核，无法再次审核")

    @allure.story("核票详情")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_expense_sheet(self, match_api, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")

        with allure.step("步骤1：查看核票详情"):
            result_json = match_api.get_detail(match_id, invoice_supplier_id)
            assert result_json["data"]["invoiceNo"] == self.invoice_no, "查询核票详情失败,发票号不匹配"

        with allure.step("步骤2：查看核票明细"):
            result_json = match_api.get_invoice_items(match_id, invoice_supplier_id)
            assert result_json["data"]["total"] > 0, "查询核票明细失败,未查询到相关数据"
            context["invoice_items"] = [
                {"id": item["id"], "itemName": item["itemName"], "itemSpec": item["spec"]}
                for item in result_json["data"]["records"]
            ]

        with allure.step("步骤3：查看费用单抵扣明细"):
            match_api.get_expense_deductions(match_id)

        with allure.step("步骤4：查看预付抵扣明细"):
            match_api.get_pre_settlement_deductions(match_id)

        with allure.step("步骤5：查看核票操作列表"):
            result_json = match_api.page_records(business_id=match_id, supplier_id=invoice_supplier_id)
            assert result_json["data"]["total"] > 0, "查询核票操作列表失败,未查询到相关数据"

    @allure.story("核票编辑")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_get_product_code(self, match_api, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")
        invoice_items = context.get("invoice_items", [])

        with allure.step("步骤1：查询商品代码"):
            result_json = match_api.get_item_units(invoice_supplier_id, "19021303858")
            assert result_json["data"]["itemName"] is not None, "查询商品代码失败,未查询到商品名称"

        with allure.step("步骤2：编辑商品代码"):
            items = [{"matchItemId": item["id"], "itemCode": get_item_code(item["itemName"], item["itemSpec"])} for item in invoice_items]
            result_json = match_api.edit_item_code(
                match_id, invoice_supplier_id, items, order_nos=self.receipt_nos
            )
            assert result_json["data"]["successCount"] == len(items), "编辑商品代码失败,成功记录数不是预期值"

    @allure.story("三单匹配-驳回")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_three_way_match_reject(self, match_api, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")
        invoice_id = context.get("invoice_id", "")

        with allure.step("步骤1：手动匹配"):
            result_json = match_api.batch_manual_match(
                [{"matchId": match_id, "invoiceId": invoice_id}],
                supplier_id=invoice_supplier_id
            )
            assert result_json["data"]["failCount"] == 0, "手动匹配失败,存在失败记录"

        with allure.step("步骤2：驳回匹配"):
            match_api.approve(match_id, approved=False, supplier_id=invoice_supplier_id)

        with allure.step("步骤3：取消匹配"):
            result_json = match_api.cancel([match_id], supplier_id=invoice_supplier_id)
            assert result_json["data"]["failCount"] == 0, "取消匹配失败,存在失败记录"

    @allure.story("三单匹配-通过")
    @pytest.mark.p0
    @pytest.mark.order(7)
    def test_07_three_way_match_pass(self, match_api, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")
        invoice_id = context.get("invoice_id", "")

        with allure.step("步骤1：手动匹配"):
            result_json = match_api.batch_manual_match(
                [{"matchId": match_id, "invoiceId": invoice_id}],
                supplier_id=invoice_supplier_id
            )
            assert result_json["data"]["failCount"] == 0, "手动匹配失败,存在失败记录"

        with allure.step("步骤2：查询未结算退款单"):
            match_api.get_unsettled_return_orders([invoice_supplier_id])

        with allure.step("步骤3：核票通过"):
            match_api.approve(match_id, approved=True, supplier_id=invoice_supplier_id)

    @allure.story("推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(8)
    def test_08_push_settlement(self, match_api, context, file_helper):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")

        with allure.step("步骤1：查询核票详情-查询推送状态"):
            result_json = match_api.page_matches(invoiceNo=self.invoice_no)
            assert result_json["data"]["total"] > 0, "查询核票数据失败,未查询到相关数据"
            assert result_json["data"]["records"][0].get("writeOffStatus") == 2,"核票状态不是已核票"
            push_status =  result_json["data"]["records"][0].get("pushStatus")

        with allure.step("步骤2：查询未结算红票"):
            result_json = match_api.pre_check_settlement(match_id, invoice_supplier_id)
            has_pending_red_invoices = result_json["data"].get("hasPendingRedInvoice", False)

        if push_status == 0 or push_status is None:
            with allure.step("步骤3：推送结算单"):
                if not has_pending_red_invoices:
                    match_api.push_settlement(match_id)
                else:
                    file_helper.append_json({"matchId": match_id,"invoiceNo": self.invoice_nos,"settleNo": "存在未结算红票，需要走红蓝对冲"}, "test.json")
                    pytest.skip("存在未结算红票，需要走红蓝对冲")

        with allure.step("步骤4：查询核票详情-验证推送结果"):
            result_json = match_api.page_matches(invoiceNo=self.invoice_no)
            assert result_json["data"]["records"][0].get("pushStatus") == 2, "推送状态不是已推送"
            settle_no = result_json["data"]["records"][0].get("settleNo")
            test_data = {
                "matchId": match_id,
                "invoiceNo": self.invoice_nos,
                "settleNo": settle_no
            }
            file_helper.append_json(test_data, "test.json")