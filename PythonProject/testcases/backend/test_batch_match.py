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
    def test_01_invoice_receive(self, admin_client, context):
        print(self.invoice_nos)
        for invoice_no in self.invoice_nos:
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/invoice/collect/byNo",
                            json={"invoiceNo": invoice_no})


    def _invoice_verify_query(self, admin_client):
        """查询票核票详情"""
        result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/page",
                          json={"pageNum": 1, "pageSize": 10, "supplierName": self.supplier_name})
        assert result_json["data"]["total"] > 0
        return result_json

    @allure.story("核票查询")
    @pytest.mark.p0
    @pytest.mark.order(2)
    def test_02_invoice_verify_query(self, admin_client, context):
        result_json = self._invoice_verify_query(admin_client)
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
    def test_03_audit_invoice(self, admin_client, context):
        invoice_ids = [item["invoice_id"] for item in context["new_invoice_data"]]
        admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/batchAudit",
                            json={"invoiceIds":invoice_ids})

    @allure.story("核票编辑")
    @pytest.mark.p0
    @pytest.mark.order(4)
    def test_04_expense_sheet(self, admin_client, context):
        new_invoice_data = context.get("new_invoice_data", [])
        for invoice_data in new_invoice_data:
            match_id = invoice_data.get("match_id", "")
            invoice_supplier_id = invoice_data.get("invoice_supplier_id", "")
            invoice_type = invoice_data.get("invoice_type", 2)
            with allure.step("步骤1：查看核票明细"):
                result_json = admin_client.send_and_validate("GET", f"/api/v1/admin/srm/three-way-match/{match_id}/invoice-items?supplierId={invoice_supplier_id}&pageNum=1&pageSize=600")
                assert result_json["data"]["total"] > 0
                invoice_item_ids = [item["id"] for item in result_json["data"]["records"]]

            with allure.step("步骤2：编辑商品代码"):
                req_data = {"matchId": match_id, "supplierId": invoice_supplier_id}
                if invoice_type == 2:
                    req_data["orderNos"] = self.receipt_nos
                    req_data["items"] = [{"matchItemId":invoice_item_ids[0],"itemCode":30306000122}]
                else:
                    req_data["returnOrderNos"] = self.return_nos
                    item_codes = ["30306000124","30306000122","104020163"]
                    req_data["items"] = [{"matchItemId":invoice_item_ids[i],"itemCode":item_codes[i]} for i in range(len(item_codes))]
                result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/item-code",
                                json=req_data)
                assert result_json["data"]["successCount"] == len(item_codes)

    @allure.story("批量三单匹配-驳回")
    @pytest.mark.p0
    @pytest.mark.order(5)
    def test_05_three_way_match_reject(self, admin_client, context):
        new_invoice_data = context.get("new_invoice_data", [])
        with allure.step("步骤1：批量匹配"):
            match_data_list = [{"matchId":item["match_id"],"invoiceId":item["invoice_id"]} for item in new_invoice_data]
            result_json1 = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/manual-match/batch",
                                json={"matchDataList":match_data_list})
            assert result_json1["data"]["failCount"] == 0

        with allure.step("步骤2：批量驳回匹配"):
            approval_data = [{"matchId":item["match_id"],"approved":False,"remark":"测试批量驳回功能"} for item in new_invoice_data]
            result_json2 = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/approval/batch",
                                json={"approvalDataList":approval_data})
            assert result_json2["data"]["failCount"] == 0

        with allure.step("步骤3：批量取消匹配"):
            match_ids = [item["match_id"] for item in new_invoice_data]
            result_json3 = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/cancel",
                                json={"matchIds":match_ids})
            assert result_json3["data"]["failCount"] == 0

    @allure.story("批量三单匹配-通过")
    @pytest.mark.p0
    @pytest.mark.order(6)
    def test_06_three_way_match_pass(self, admin_client, context):
        new_invoice_data = context.get("new_invoice_data", [])
        with allure.step("步骤1：批量匹配"):
            match_data_list = [{"matchId":item["match_id"],"invoiceId":item["invoice_id"]} for item in new_invoice_data]
            result_json1 = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/manual-match/batch",
                                json={"matchDataList":match_data_list})
            assert result_json1["data"]["failCount"] == 0

        with allure.step("步骤2：批量通过匹配"):
            approval_data = [{"matchId": item["match_id"], "approved": True, "remark": "测试批量审核通过"} for item in
                             new_invoice_data]
            result_json2 = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/approval/batch",
                                                          json={"approvalDataList": approval_data})
            assert result_json2["data"]["failCount"] == 0


    @allure.story("批量推送结算单")
    @pytest.mark.p0
    @pytest.mark.order(7)
    def test_07_push_settlement(self, admin_client, context, file_helper):
        new_invoice_data = context.get("new_invoice_data", [])
        with allure.step("步骤1：查询未结算红票"):
            supplier_ids = list({item["invoice_supplier_id"] for item in new_invoice_data})
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/push-settlement/red-block-check",
                                json={supplier_ids})

        with allure.step("步骤2：推送结算单"):
            req_data = {"matchIds": [], "redMatchIds": []}
            for item in new_invoice_data:
                if item["invoice_type"] == 2:
                    req_data["matchIds"].append(item["match_id"])
                else:
                    req_data["redMatchIds"].append(item["match_id"])
            admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/push-settlement/batch",
                                json=req_data)

        with allure.step("步骤3：查询核票详情-验证推送结果"):
            for item in new_invoice_data:
                invoice_no = item["invoice_no"]
                result_json = admin_client.send_and_validate("POST", "/api/v1/admin/srm/three-way-match/page",
                                                             json={"pageNum": 1, "pageSize": 10,
                                                                   "invoiceNo": invoice_no})
                settle_no = result_json["data"].get("records", [])[0].get("settleNo")
                test_data = {
                    "matchId": item["match_id"],
                    "invoiceNo": invoice_no,
                    "settleNo": settle_no
                }
                file_helper.append_json(test_data, "test.json")
