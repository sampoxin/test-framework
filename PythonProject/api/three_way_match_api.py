"""三单匹配业务 API Object - 统一管理发票、核票、强制匹配、操作记录所有接口"""
from api.base_api import BaseApi


class ThreeWayMatchApi(BaseApi):
    """后台三单匹配业务统一 API（发票管理 + 核票匹配 + 强制匹配 + 操作记录）"""

    # ==================== 发票管理 ====================

    def collect_invoice(self, invoice_no: str) -> dict:
        """按发票号码收取发票"""
        return self._post("/api/v1/admin/srm/invoice/collect/byNo", json={"invoiceNo": invoice_no})

    def page_invoices(self, page_num: int = 1, page_size: int = 10, **filters) -> dict:
        """分页查询发票列表，支持任意筛选条件"""
        params = {"pageNum": page_num, "pageSize": page_size, **filters}
        return self._post("/api/v1/admin/srm/invoice/page", json=params)

    def get_invoice_detail(self, invoice_id) -> dict:
        """获取发票详情"""
        return self._get(f"/api/v1/admin/srm/invoice/detail/{invoice_id}")

    # ==================== 核票查询 ====================

    def page_matches(self, page_num: int = 1, page_size: int = 10, **filters) -> dict:
        """分页查询核票列表（支持 invoiceNo/matchId/supplierName 等筛选）"""
        params = {"pageNum": page_num, "pageSize": page_size, **filters}
        return self._post("/api/v1/admin/srm/three-way-match/page", json=params)

    def get_detail(self, match_id, supplier_id) -> dict:
        """获取核票详情"""
        return self._get(f"/api/v1/admin/srm/three-way-match/detail/{match_id}?supplierId={supplier_id}")

    def get_invoice_items(self, match_id, supplier_id, page_num: int = 1, page_size: int = 600) -> dict:
        """获取核票明细行"""
        return self._get(
            f"/api/v1/admin/srm/three-way-match/{match_id}/invoice-items"
            f"?supplierId={supplier_id}&pageNum={page_num}&pageSize={page_size}"
        )

    # ==================== 审核 ====================

    def audit_invoice(self, invoice_id, audit_status: int = 2) -> dict:
        """审核发票（audit_status: 1=待审核, 2=已审核）"""
        return self._post("/api/v1/admin/srm/three-way-match/audit", json={"id": invoice_id, "auditStatus": audit_status})

    def batch_audit(self, invoice_ids: list) -> dict:
        """批量审核发票"""
        return self._post("/api/v1/admin/srm/three-way-match/batchAudit", json={"invoiceIds": invoice_ids})

    # ==================== 匹配操作 ====================

    def batch_manual_match(self, match_data_list: list, supplier_id=None) -> dict:
        """
        批量手动匹配
        match_data_list: [{"matchId": ..., "invoiceId": ...}, ...]
        """
        params = {"matchDataList": match_data_list}
        if supplier_id:
            params["supplierId"] = supplier_id
        return self._post("/api/v1/admin/srm/three-way-match/manual-match/batch", json=params)

    def approve(self, match_id, approved: bool, supplier_id=None, remark: str = "") -> dict:
        """单条匹配审批（通过/驳回）"""
        params = {"matchId": match_id, "approved": approved}
        if supplier_id:
            params["supplierId"] = supplier_id
        if remark:
            params["remark"] = remark
        return self._post("/api/v1/admin/srm/three-way-match/approval", json=params)

    def batch_approve(self, approval_data_list: list) -> dict:
        """
        批量审批
        approval_data_list: [{"matchId": ..., "approved": True/False, "remark": "..."}, ...]
        """
        return self._post("/api/v1/admin/srm/three-way-match/approval/batch", json={"approvalDataList": approval_data_list})

    def cancel(self, match_ids: list, supplier_id=None) -> dict:
        """取消匹配"""
        params = {"matchIds": match_ids}
        if supplier_id:
            params["supplierId"] = supplier_id
        return self._post("/api/v1/admin/srm/three-way-match/cancel", json=params)

    # ==================== 编辑 ====================

    def edit_item_code(self, match_id, supplier_id, items: list, order_nos: list = None, return_order_nos: list = None) -> dict:
        """
        编辑商品代码
        items: [{"matchItemId": ..., "itemCode": ...}, ...]
        """
        params = {"matchId": match_id, "supplierId": supplier_id, "items": items}
        if order_nos:
            params["orderNos"] = order_nos
        if return_order_nos:
            params["returnOrderNos"] = return_order_nos
        return self._post("/api/v1/admin/srm/three-way-match/item-code", json=params)

    def get_item_units(self, supplier_id, item_code: str) -> dict:
        """查询商品代码的单位信息"""
        return self._post("/api/v1/admin/srm/three-way-match/item-units", json={"supplierId": supplier_id, "itemCode": item_code})

    # ==================== 抵扣明细 ====================

    def get_expense_deductions(self, match_id) -> dict:
        """查看费用单抵扣明细"""
        return self._get(f"/api/v1/admin/srm/three-way-match/{match_id}/expense-order-deductions")

    def get_pre_settlement_deductions(self, match_id) -> dict:
        """查看预付抵扣明细"""
        return self._get(f"/api/v1/admin/srm/three-way-match/{match_id}/pre-settlement-deductions")

    def get_make_up_orders(self, match_id) -> dict:
        """查看乐檬扣补单明细"""
        return self._get(f"/api/v1/admin/srm/three-way-match/{match_id}/make-up-orders")

    def get_unsettled_return_orders(self, supplier_ids: list) -> dict:
        """查询未结算退货单"""
        ids_param = ",".join(str(s) for s in supplier_ids)
        return self._get(f"/api/v1/admin/srm/three-way-match/unsettled-return-orders?supplierIds={ids_param}")

    # ==================== 推送结算 ====================

    def push_settlement(self, match_id) -> dict:
        """单条推送结算单"""
        return self._post(f"/api/v1/admin/srm/three-way-match/{match_id}/push-settlement", json={})

    def batch_push_settlement(self, match_ids: list = None, red_match_ids: list = None) -> dict:
        """批量推送结算单"""
        params = {"matchIds": match_ids or [], "redMatchIds": red_match_ids or []}
        return self._post("/api/v1/admin/srm/three-way-match/push-settlement/batch", json=params)

    def pre_check_settlement(self, match_id, supplier_id) -> dict:
        """推送前检查（是否有未结算红票）"""
        return self._get(f"/api/v1/admin/srm/three-way-match/{match_id}/push-settlement/pre-check?supplierId={supplier_id}")

    def check_red_block(self, supplier_ids: list) -> dict:
        """查询未结算红票（红蓝对冲检查）"""
        return self._post("/api/v1/admin/srm/three-way-match/push-settlement/red-block-check", json=list(supplier_ids))

    # ==================== 强制匹配 ====================

    def get_supplier_options(self, keyword: str = None, limit: int = 20) -> dict:
        """搜索供应商选项"""
        params = {"limit": limit}
        if keyword:
            params["keyword"] = keyword
        return self._post("/api/v1/admin/srm/force-match/supplier-options", json=params)

    def page_unsettled(self, supplier_id, page_num: int = 1, page_size: int = 20,
                       order_nos: list = None, receipt_nos: list = None, return_nos: list = None) -> dict:
        """分页查询未结算收/退货单"""
        params = {"supplierId": supplier_id, "pageNum": page_num, "pageSize": page_size}
        if order_nos:
            params["orderNos"] = order_nos
        if receipt_nos:
            params["receiptNos"] = receipt_nos
        if return_nos:
            params["returnNos"] = return_nos
        return self._post("/api/v1/admin/srm/force-match/page-unsettled", json=params)

    def load_receipt_items(self, supplier_id, receipt_nos: list = None, return_nos: list = None) -> dict:
        """读取未结算收/退货单详情（商品明细）"""
        params = {"supplierId": supplier_id}
        if receipt_nos:
            params["receiptNos"] = receipt_nos
        if return_nos:
            params["returnNos"] = return_nos
        return self._post("/api/v1/admin/srm/force-match/load-receipt-items", json=params)

    def check_invoice_summary(self, supplier_id, invoice_nos: list) -> dict:
        """校验发票信息（冲突检查）"""
        return self._post("/api/v1/admin/srm/force-match/invoice-summary", json={
            "supplierId": supplier_id, "invoiceNos": invoice_nos
        })

    def submit_force_match(self, supplier_id, invoice_nos: list, receipt_or_return_nos: list,
                           items: list, tab: str = None) -> dict:
        """提交强制匹配生成发票"""
        params = {
            "supplierId": supplier_id,
            "invoiceNos": invoice_nos,
            "receiptOrReturnNos": receipt_or_return_nos,
            "items": items,
        }
        if tab:
            params["tab"] = tab
        return self._post("/api/v1/admin/srm/force-match/submit", json=params)

    def get_force_result(self, force_batch_no) -> dict:
        """查看强制匹配结果"""
        return self._get(f"/api/v1/admin/srm/force-match/result/{force_batch_no}")

    # ==================== 操作记录 ====================

    def page_records(self, business_id, supplier_id=None, business_type: int = None,
                     page_num: int = 1, page_size: int = 10, sort: str = "DESC") -> dict:
        """分页查询操作记录"""
        params = {"businessId": business_id, "pageNum": page_num, "pageSize": page_size, "sort": sort}
        if supplier_id:
            params["supplierId"] = supplier_id
        if business_type is not None:
            params["businessType"] = business_type
        return self._post("/api/v1/admin/srm/operation-record/page", json=params)
