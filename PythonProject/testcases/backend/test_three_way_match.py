"""三单匹配-人工匹配正常流程（收票-核票-匹配-推送结算单）"""
import allure
import pytest

@allure.epic("三单匹配")
@allure.feature("收票核票")
@pytest.mark.parametrize("setup_test_data",["data_1"],indirect=True)
class TestThreeWayMatch:
    @allure.story("收票")
    @pytest.mark.p0
    @pytest.mark.order(1)
    def test_01_invoice_receive(self, admin_client, context):
        with allure.step("步骤1：收取发票"):
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/invoice/collect/byNo",
                                json={"invoiceNo": self.invoice_no})

        with allure.step("步骤2：查询发票"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/invoice/page",
                                json={"pageNum":1,"pageSize":10,"invoiceNo":self.invoice_no})
            assert result_json["data"]["total"] > 0
            assert result_json["data"]["records"][0]["invoiceNo"] == self.invoice_no
            context["invoice_id"] = result_json["data"]["records"][0]["id"]

        with allure.step("步骤3：查看收票详情"):
            result_json = admin_client.send_and_validate("GET", f"/api/v1/admin/srm/invoice/detail/{context['invoice_id']}")
            assert result_json["data"]["invoiceNo"] == self.invoice_no

        with allure.step("步骤4：查看收票操作列表"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/operation-record/page",
                                json={"businessType":2,"businessId":context["invoice_id"],"pageNum":1,"pageSize":1,"sort":"DESC"})
            assert result_json["data"]["total"] > 0

    def _invoice_verify_query(self, admin_client, context, invoice_no):
        """查询票核票详情"""
        result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/page",
                          json={"pageNum": 1, "pageSize": 10, "invoiceNo": invoice_no})
        assert result_json["data"]["total"] > 0
        context["match_id"] = result_json["data"].get("records", [])[0].get("id")
        context["invoice_supplier_id"] = result_json["data"].get("records", [])[0].get("supplierId")
        context["invoice_id"] = result_json["data"]["records"][0].get("invoiceId")
        context["invoice_audit_status"] = result_json["data"].get("records", [])[0].get("auditStatus")
        context["invoice_push_status"] = result_json["data"].get("records", [])[0].get("pushStatus")
        return result_json

    @allure.story("核票查询")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_invoice_verify_query(self, admin_client, context):
        self._invoice_verify_query(admin_client, context, self.invoice_no)

    @allure.story("审核发票")
    @pytest.mark.p0
    @pytest.mark.order(3)
    def test_03_audit_invoice(self, admin_client, context):
        audit_status = context.get("invoice_audit_status", 1)
        if audit_status != 2:
            invoice_id = context.get("invoice_id", "")
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/audit",
                                json={"id":invoice_id,"auditStatus":2})
        else:
            pytest.skip(f"发票已审核，无法再次审核")

    @allure.story("核票详情")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_expense_sheet(self, admin_client, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")

        with allure.step("步骤1：查看核票详情"):
            result_json = admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/detail/{match_id}?supplierId={invoice_supplier_id}")
            assert result_json["data"]["invoiceNo"] == self.invoice_no

        with allure.step("步骤2：查看核票明细"):
            result_json = admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/invoice-items?supplierId={invoice_supplier_id}&pageNum=1&pageSize=600")
            assert result_json["data"]["total"] > 0
            context["invoice_item_ids"] = [item["id"] for item in result_json["data"]["records"]]

        with allure.step("步骤3：查看费用单抵扣明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/expense-order-deductions")

        with allure.step("步骤4：查看预付抵扣明细"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/pre-settlement-deductions")

        with allure.step("步骤5：查看核票操作列表"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/operation-record/page",
                                json={"businessId":match_id,"supplierId":invoice_supplier_id})
            assert result_json["data"]["total"] > 0

    @allure.story("核票编辑")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_get_product_code(self, admin_client, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")

        with allure.step("步骤1：查询商品代码"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/item-units",
                                json={"supplierId":invoice_supplier_id,"itemCode":"19021303858"})
            assert result_json["data"]["itemName"] is not None

        with allure.step("步骤2：编辑商品代码"):
            req_data = {"matchId":match_id,
                        "supplierId":invoice_supplier_id,
                        "orderNos":self.receipt_nos
                        }
            invoice_item_ids = context.get("invoice_item_ids", [])
            item_codes = ["19021303854","19021100480","19021303858","19021303856"]
            req_data["items"] = [{"matchItemId":invoice_item_ids[i],"itemCode":item_codes[i]} for i in range(4)]
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/item-code",
                                json=req_data)
            assert result_json["data"]["successCount"] == 4

    @allure.story("三单匹配-驳回")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_three_way_match_reject(self, admin_client, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")
        invoice_id = context.get("invoice_id", "")

        with allure.step("步骤1：手动匹配"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/manual-match/batch",
                                json={"matchDataList":[{"matchId":match_id,"invoiceId":invoice_id}],"supplierId":invoice_supplier_id})
            assert result_json["data"]["failCount"] == 0

        with allure.step("步骤2：驳回匹配"):
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/approval",
                                json={"matchId":match_id,"approved":False,"supplierId":invoice_supplier_id})

        with allure.step("步骤3：取消匹配"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/cancel",
                                json={"matchIds":[match_id],"supplierId":invoice_supplier_id})
            assert result_json["data"]["failCount"] == 0

    @allure.story("三单匹配-通过")
    @pytest.mark.p0
    @pytest.mark.order(7)
    def test_07_three_way_match_pass(self, admin_client, context):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")
        invoice_id = context.get("invoice_id", "")

        with allure.step("步骤1：手动匹配"):
            result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/manual-match/batch",
                                json={"matchDataList":[{"matchId":match_id,"invoiceId":invoice_id}],"supplierId":invoice_supplier_id})
            assert result_json["data"]["failCount"] == 0

        with allure.step("步骤2：查询未结算退款单"):
            admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/unsettled-return-orders?supplierIds={invoice_supplier_id}")

        with allure.step("步骤3：核票通过"):
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/approval",
                                json={"matchId":match_id,"approved":True,"supplierId":invoice_supplier_id})



    @allure.story("推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(8)
    def test_08_push_settlement(self, admin_client, context, file_helper):
        match_id = context.get("match_id", "")
        invoice_supplier_id = context.get("invoice_supplier_id", "")

        with allure.step("步骤1：查询核票详情-查询推送状态"):
            self._invoice_verify_query(admin_client, context, self.invoice_no)
            invoice_push_status = context["invoice_push_status"]

        with allure.step("步骤2：查询未结算红票"):
            result_json = admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/push-settlement/pre-check?supplierId={invoice_supplier_id}")
            has_pending_red_invoices = result_json["data"].get("hasPendingRedInvoice", False)

        if invoice_push_status == 0 or invoice_push_status is None:
            with allure.step("步骤3：推送结算单"):
                if not has_pending_red_invoices:
                    admin_client.send_and_validate("POST", f"/api/v1/admin/srm/three-way-match/{match_id}/push-settlement",
                                        json={})
                else:
                    pytest.step("存在未结算红票，需要走红蓝对冲")

        with allure.step("步骤4：查询核票详情-验证推送结果"):
            result_json = self._invoice_verify_query(admin_client, context, self.invoice_no)
            assert context["invoice_push_status"] == 2
            settle_no = result_json["data"].get("records", [])[0].get("settleNo")
            test_data = {
                "matchId": match_id,
                "invoiceNo": self.invoice_nos,
                "settleNo": settle_no
            }
            file_helper.append_json(test_data, "test.json")