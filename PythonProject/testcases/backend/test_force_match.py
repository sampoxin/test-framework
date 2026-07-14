"""三单匹配-强制匹配正常流程（收票-强制匹配-推送结算单）"""

import allure
import pytest

from utils.assemble_data import convert_receipt_data


@allure.epic("三单匹配")
@allure.feature("强制匹配")
@pytest.mark.parametrize("setup_test_data",["data_2","data_5"],indirect=True)
class TestForceMatch:

    def _invoice_verify_query(self, admin_client, context, match_id):
        """查询票核票详情"""
        result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/page",
                          json={"pageNum":1,"pageSize":10,"matchId":match_id})
        assert result_json["data"]["total"] > 0
        context["invoice_push_status"] = result_json["data"].get("records", [])[0].get("pushStatus")
        return result_json

    @allure.story("收票/审核")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_invoice_receive(self, admin_client, context):
        with allure.step("步骤1：收取发票"):
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/invoice/collect/byNo",
                                       json={"invoiceNo": self.invoice_no})

        with allure.step("步骤2：查询发票"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/page",
                                       json={"pageNum": 1, "pageSize": 10, "invoiceNo": self.invoice_no})
            assert result_json["data"]["total"] > 0
            context["match_id"] = result_json["data"].get("records", [])[0].get("id")
            invoice_id = result_json["data"]["records"][0].get("invoiceId")
            audit_status = result_json["data"].get("records", [])[0].get("auditStatus")

        with allure.step("步骤3：审核发票"):
            if audit_status != 2:
                admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/audit",
                                           json={"id": invoice_id, "auditStatus": 2})
            else:
                pytest.skip(f"发票已审核，无法再次审核")


    @allure.story("查询未结算收/退货单")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_query_unsettled_match(self, admin_client, context):
        with allure.step("步骤1：搜索供应商"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/supplier-options",
                                json={"limit":20})
            assert len(result_json["data"]) == 20

        with allure.step("步骤2：搜索指定供应商"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/supplier-options",
                                json={"keyword":self.supplier_name,"limit":20})
            assert result_json["data"][0]["supplierName"] == self.supplier_name
            context["supplier_id"] = result_json["data"][0]["supplierId"]

        with allure.step("步骤3：搜索指定供应商的未结算收/退货单"):
            supplier_id = context["supplier_id"]
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/page-unsettled",
                                json={"supplierId":supplier_id,"pageNum":1,"pageSize":20,"orderNos":self.receipt_nos})
            assert result_json["data"]["total"] > 0
            context["receipt_nos"] = [item["receiptOrReturnNo"] for item in result_json["data"]["records"]]

    @allure.story("生成发票")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_generate_invoice(self, admin_client, context):
        supplier_id = context["supplier_id"]
        receipt_nos = context["receipt_nos"]

        with allure.step("步骤1：读取未结算收/退货单详情"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/load-receipt-items",
                                json={"supplierId":supplier_id,"receiptNos":receipt_nos})
            assert len(result_json["data"]["receiptItems"]) >= len(receipt_nos)
            receipt_items = convert_receipt_data(result_json)

        with allure.step("步骤2：校验发票信息"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/invoice-summary",
                                json={"supplierId":supplier_id,"invoiceNos":self.invoice_nos})
            assert result_json["data"]["conflictReasons"] == []

        with allure.step("步骤3：生成发票"):
            self._generate_invoice( admin_client, context, self.invoice_nos, supplier_id, receipt_nos, receipt_items)


    def _generate_invoice(self, admin_client, context, invoice_nos, supplier_id, receipt_nos, receipt_items):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/force-match/submit",
                                json={"tab":"RECEIPT","supplierId":supplier_id,"invoiceNos":invoice_nos,"receiptOrReturnNos":receipt_nos,"items":receipt_items})
            context["match_ids"] = result_json["data"]["matchIds"]

    @allure.story("核票详情")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_invoice_verify(self, admin_client, context):
        match_id = context.get("match_ids", "")[0]
        supplier_id = context.get("supplier_id", "")
        with allure.step("步骤1：查看核票详情"):
            result_json = admin_client.send_and_validate("GET",
                                       f"/api/v1/admin/srm/three-way-match/detail/{match_id}?supplierId={supplier_id}")
            assert result_json["data"]["invoiceNo"] in self.invoice_nos
            force_batch_no = result_json["data"]["forceBatchNo"]

        with allure.step("步骤2：查看核票明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/force-match/result/{force_batch_no}")

        with allure.step("步骤3：查看费用单抵扣明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/expense-order-deductions")

        with allure.step("步骤4：查看预付抵扣明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/pre-settlement-deductions")

        with allure.step("步骤5：查看核票操作列表"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/operation-record/page",
                                       json={"businessId": match_id, "supplierId": supplier_id})
            assert result_json["data"]["total"] > 0

        with allure.step("步骤6：查看乐檬扣补单明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/make-up-orders")

    @allure.story("核票通过")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_approval_pass(self, admin_client, context):
        match_id = context.get("match_ids", "")[0]
        supplier_id = context.get("supplier_id", "")
        admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/approval",
                                   json={"matchId": match_id, "approved": True, "supplierId": supplier_id})

    @allure.story("推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_push_settlement(self, admin_client, context, file_helper):
        match_ids = context.get("match_ids", "")
        supplier_id = context.get("supplier_id", "")

        with allure.step("步骤1：查询核票详情-查询推送状态"):
            self._invoice_verify_query(admin_client, context, match_ids[0])
            invoice_push_status = context["invoice_push_status"]

        with allure.step("步骤2：查询未结算红票"):
            result_json = admin_client.send_and_validate("GET",
                                       f"/api/v1/admin/srm/three-way-match/{match_ids[0]}/push-settlement/pre-check?supplierId={supplier_id}")
            has_pending_red_invoices = result_json["data"].get("hasPendingRedInvoice", False)

        if invoice_push_status == 0 or invoice_push_status is None:
            with allure.step("步骤3：推送结算单"):
                if not has_pending_red_invoices:
                    admin_client.send_and_validate("POST", f"/api/v1/admin/srm/three-way-match/{match_ids[0]}/push-settlement",
                                               json={})
                else:
                    pytest.step("存在未结算红票，需要走红蓝对冲")

        with allure.step("步骤4：查询核票详情-验证推送结果"):
            result_json = self._invoice_verify_query(admin_client, context, match_ids[0])
            assert context["invoice_push_status"] == 2
            settle_no = result_json["data"].get("records", [])[0].get("settleNo")
            test_data = {
                "matchId": match_ids,
                "invoiceNo": self.invoice_nos,
                "settleNo": settle_no
            }
            file_helper.append_json(test_data, "test.json")
