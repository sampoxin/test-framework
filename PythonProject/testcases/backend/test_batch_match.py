"""三单匹配-批量操作正常流程（收票-核票-匹配-推送结算单）"""
import allure
import pytest


@allure.epic("三单匹配")
@allure.feature("批量操作")
class TestBatchMatch:
    DATA_KEY = "data_4"

    @allure.story("收票")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_invoice_receive(self, match_api):
        print(self.invoice_nos)
        for invoice_no in self.invoice_nos:
            match_api.collect_invoice(invoice_no)

    @allure.story("核票查询")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_invoice_verify_query(self, match_api, context):
        result_json = match_api.page_matches(supplierName=self.supplier_name)
        assert result_json["data"]["total"] > 0, "查询核票失败,未查询到相关数据"
        context["new_invoice_data"] = []
        for item in result_json["data"]["records"]:
            if item["invoiceNo"] in self.invoice_nos:
                invoice_data = {
                    "match_id": item["id"],
                    "invoice_no": item["invoiceNo"],
                    "invoice_id": item["invoiceId"],
                    "invoice_type": item["invoiceType"],
                    "invoice_supplier_id": item["supplierId"]
                }
                context["new_invoice_data"].append(invoice_data)

    @allure.story("批量审核发票")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_audit_invoice(self, match_api, context):
        invoice_ids = [item["invoice_id"] for item in context["new_invoice_data"]]
        match_api.batch_audit(invoice_ids)

    @allure.story("核票编辑")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_expense_sheet(self, match_api, context):
        new_invoice_data = context.get("new_invoice_data", [])
        for invoice_data in new_invoice_data:
            match_id = invoice_data["match_id"]
            invoice_supplier_id = invoice_data["invoice_supplier_id"]
            invoice_type = invoice_data.get("invoice_type", 2)

            with allure.step("步骤1：查看核票明细"):
                result_json = match_api.get_invoice_items(match_id, invoice_supplier_id)
                assert result_json["data"]["total"] > 0, "查询核票明细失败,未查询到相关数据"
                invoice_item_ids = [item["id"] for item in result_json["data"]["records"]]

            with allure.step("步骤2：编辑商品代码"):
                if invoice_type == 2:
                    item_codes = ["30306000122"]
                    items = [{"matchItemId": invoice_item_ids[0], "itemCode": 30306000122}]
                    result_json = match_api.edit_item_code(
                        match_id, invoice_supplier_id, items, order_nos=self.receipt_nos
                    )
                else:
                    item_codes = ["30306000124", "30306000122", "104020163"]
                    items = [{"matchItemId": invoice_item_ids[i], "itemCode": item_codes[i]} for i in range(len(item_codes))]
                    result_json = match_api.edit_item_code(
                        match_id, invoice_supplier_id, items, return_order_nos=self.return_nos
                    )
                assert result_json["data"]["successCount"] == len(item_codes), "批量编辑商品代码失败,存在失败记录"

    @allure.story("批量三单匹配-驳回")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_three_way_match_reject(self, match_api, context):
        new_invoice_data = context.get("new_invoice_data", [])

        with allure.step("步骤1：批量匹配"):
            match_data_list = [{"matchId": item["match_id"], "invoiceId": item["invoice_id"]} for item in new_invoice_data]
            result_json = match_api.batch_manual_match(match_data_list)
            assert result_json["data"]["failCount"] == 0, "批量匹配失败,存在失败记录"

        with allure.step("步骤2：批量驳回匹配"):
            approval_data = [{"matchId": item["match_id"], "approved": False, "remark": "测试批量驳回功能"} for item in new_invoice_data]
            result_json = match_api.batch_approve(approval_data)
            assert result_json["data"]["failCount"] == 0, "批量驳回匹配失败,存在失败记录"

        with allure.step("步骤3：批量取消匹配"):
            match_ids = [item["match_id"] for item in new_invoice_data]
            result_json = match_api.cancel(match_ids)
            assert result_json["data"]["failCount"] == 0, "批量取消匹配失败,存在失败记录"

    @allure.story("批量三单匹配-通过")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_three_way_match_pass(self, match_api, context):
        new_invoice_data = context.get("new_invoice_data", [])

        with allure.step("步骤1：批量匹配"):
            match_data_list = [{"matchId": item["match_id"], "invoiceId": item["invoice_id"]} for item in new_invoice_data]
            result_json = match_api.batch_manual_match(match_data_list)
            assert result_json["data"]["failCount"] == 0, "批量匹配失败,存在失败记录"

        with allure.step("步骤2：批量通过匹配"):
            approval_data = [{"matchId": item["match_id"], "approved": True, "remark": "测试批量审核通过"} for item in new_invoice_data]
            result_json = match_api.batch_approve(approval_data)
            assert result_json["data"]["failCount"] == 0, "批量通过匹配失败,存在失败记录"

    @allure.story("批量推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(7)
    def test_07_push_settlement(self, match_api, context, file_helper):
        new_invoice_data = context.get("new_invoice_data", [])

        with allure.step("步骤1：查询未结算红票"):
            supplier_ids = list({item["invoice_supplier_id"] for item in new_invoice_data})
            match_api.check_red_block(supplier_ids)

        with allure.step("步骤2：推送结算单"):
            match_ids = []
            red_match_ids = []
            for item in new_invoice_data:
                if item["invoice_type"] == 2:
                    match_ids.append(item["match_id"])
                else:
                    red_match_ids.append(item["match_id"])
            match_api.batch_push_settlement(match_ids, red_match_ids)

        with allure.step("步骤3：查询核票详情-验证推送结果"):
            for item in new_invoice_data:
                invoice_no = item["invoice_no"]
                result_json = match_api.page_matches(invoiceNo=invoice_no)
                settle_no = result_json["data"]["records"][0].get("settleNo", "")
                test_data = {
                    "matchId": item["match_id"],
                    "invoiceNo": invoice_no,
                    "settleNo": settle_no
                }
                file_helper.append_json(test_data, "test.json")
