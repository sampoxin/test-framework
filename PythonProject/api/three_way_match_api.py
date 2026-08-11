"""三单匹配业务 API Object - 统一管理发票、核票、强制匹配、操作记录所有接口"""
from api.base_api import BaseApi
from utils.schema_validator import (
    STANDARD_RESPONSE,
    PAGE_RESPONSE,
    BATCH_RESULT_RESPONSE,
    LIST_DATA_RESPONSE,
    OBJECT_DATA_RESPONSE,
    BOOL_DATA_RESPONSE,
    ITEM_CODE_RESPONSE,
    THREE_WAY_MATCH_PAGE_RESPONSE,
    THREE_WAY_MATCH_DETAIL_RESPONSE,
)


class ThreeWayMatchApi(BaseApi):
    """后台三单匹配业务统一 API（发票管理 + 核票匹配 + 强制匹配 + 操作记录）"""

    # ==================== URL 前缀常量 ====================
    _INVOICE = "/api/v1/admin/srm/invoice"
    _MATCH = "/api/v1/admin/srm/three-way-match"
    _FORCE = "/api/v1/admin/srm/force-match"
    _RECORD = "/api/v1/admin/srm/operation-record"

    # ==================== 发票管理 ====================

    def collect_invoice(self, invoice_no: str) -> dict:
        """按发票号码收取发票"""
        return self._post(f"{self._INVOICE}/collect/byNo", schema=OBJECT_DATA_RESPONSE,
                          json={"invoiceNo": invoice_no})

    def page_invoices(self, page_num: int = 1, page_size: int = 10, **filters) -> dict:
        """分页查询发票列表，支持任意筛选条件"""
        params = {"pageNum": page_num, "pageSize": page_size, **filters}
        return self._post(f"{self._INVOICE}/page", schema=PAGE_RESPONSE, json=params)

    def get_invoice_detail(self, invoice_id) -> dict:
        """获取发票详情"""
        return self._get(f"{self._INVOICE}/detail/{invoice_id}", schema=OBJECT_DATA_RESPONSE)

    # ==================== 核票查询 ====================

    def page_matches(self, page_num: int = 1, page_size: int = 10, **filters) -> dict:
        """分页查询核票列表（支持 invoiceNo/matchId/supplierName 等筛选）"""
        params = {"pageNum": page_num, "pageSize": page_size, **filters}
        return self._post(f"{self._MATCH}/page", schema=THREE_WAY_MATCH_PAGE_RESPONSE, json=params)

    def get_detail(self, match_id, supplier_id) -> dict:
        """获取核票详情"""
        return self._get(f"{self._MATCH}/detail/{match_id}?supplierId={supplier_id}",
                         schema=THREE_WAY_MATCH_DETAIL_RESPONSE)

    def get_invoice_items(self, match_id, supplier_id, page_num: int = 1, page_size: int = 600) -> dict:
        """获取核票明细行"""
        return self._get(
            f"{self._MATCH}/{match_id}/invoice-items"
            f"?supplierId={supplier_id}&pageNum={page_num}&pageSize={page_size}",
            schema=OBJECT_DATA_RESPONSE,
        )

    # ==================== 审核 ====================

    def audit_invoice(self, invoice_id, audit_status: int = 2) -> dict:
        """审核发票（audit_status: 1=待审核, 2=已审核）"""
        return self._post(f"{self._MATCH}/audit", schema=BATCH_RESULT_RESPONSE,
                          json={"id": invoice_id, "auditStatus": audit_status})

    def batch_audit(self, invoice_ids: list) -> dict:
        """批量审核发票"""
        return self._post(f"{self._MATCH}/batchAudit", schema=BATCH_RESULT_RESPONSE,
                          json={"invoiceIds": invoice_ids})

    # ==================== 匹配操作 ====================

    def batch_manual_match(self, match_data_list: list, supplier_id=None) -> dict:
        """
        批量手动匹配
        match_data_list: [{"matchId": ..., "invoiceId": ...}, ...]
        """
        params = {"matchDataList": match_data_list}
        if supplier_id:
            params["supplierId"] = supplier_id
        return self._post(f"{self._MATCH}/manual-match/batch", schema=BATCH_RESULT_RESPONSE, json=params)

    def approve(self, match_id, approved: bool, supplier_id=None, remark: str = "") -> dict:
        """单条匹配审批（通过/驳回）"""
        params = {"matchId": match_id, "approved": approved}
        if supplier_id:
            params["supplierId"] = supplier_id
        if remark:
            params["remark"] = remark
        # 单条审批 data 为 null（日志实测），只校包装层
        return self._post(f"{self._MATCH}/approval", schema=STANDARD_RESPONSE, json=params)

    def batch_approve(self, approval_data_list: list) -> dict:
        """
        批量审批
        approval_data_list: [{"matchId": ..., "approved": True/False, "remark": "..."}, ...]
        """
        return self._post(f"{self._MATCH}/approval/batch", schema=BATCH_RESULT_RESPONSE,
                          json={"approvalDataList": approval_data_list})

    def cancel(self, match_ids: list, supplier_id=None) -> dict:
        """取消匹配"""
        params = {"matchIds": match_ids}
        if supplier_id:
            params["supplierId"] = supplier_id
        return self._post(f"{self._MATCH}/cancel", schema=BATCH_RESULT_RESPONSE, json=params)

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
        return self._post(f"{self._MATCH}/item-code", schema=ITEM_CODE_RESPONSE, json=params)

    def get_item_units(self, supplier_id, item_code: str) -> dict:
        """查询商品代码的单位信息"""
        return self._post(f"{self._MATCH}/item-units", schema=OBJECT_DATA_RESPONSE,
                          json={"supplierId": supplier_id, "itemCode": item_code})

    # ==================== 抵扣明细 ====================

    def get_expense_deductions(self, match_id) -> dict:
        """查看费用单抵扣明细"""
        return self._get(f"{self._MATCH}/{match_id}/expense-order-deductions", schema=OBJECT_DATA_RESPONSE)

    def get_pre_settlement_deductions(self, match_id) -> dict:
        """查看预付抵扣明细"""
        return self._get(f"{self._MATCH}/{match_id}/pre-settlement-deductions", schema=OBJECT_DATA_RESPONSE)

    def get_make_up_orders(self, match_id) -> dict:
        """查看乐檬扣补单明细"""
        return self._get(f"{self._MATCH}/{match_id}/make-up-orders", schema=LIST_DATA_RESPONSE)

    def get_unsettled_return_orders(self, supplier_ids: list) -> dict:
        """查询未结算退货单"""
        ids_param = ",".join(str(s) for s in supplier_ids)
        return self._get(f"{self._MATCH}/unsettled-return-orders?supplierIds={ids_param}",
                         schema=OBJECT_DATA_RESPONSE)

    # ==================== 推送结算 ====================

    def push_settlement(self, match_id) -> dict:
        """单条推送结算单"""
        return self._post(f"{self._MATCH}/{match_id}/push-settlement", schema=BOOL_DATA_RESPONSE, json={})

    def batch_push_settlement(self, match_ids: list = None, red_match_ids: list = None) -> dict:
        """批量推送结算单"""
        params = {"matchIds": match_ids or [], "redMatchIds": red_match_ids or []}
        return self._post(f"{self._MATCH}/push-settlement/batch", schema=BATCH_RESULT_RESPONSE, json=params)

    def pre_check_settlement(self, match_id, supplier_id) -> dict:
        """推送前检查（是否有未结算红票）"""
        return self._get(f"{self._MATCH}/{match_id}/push-settlement/pre-check?supplierId={supplier_id}",
                         schema=OBJECT_DATA_RESPONSE)

    def check_red_block(self, supplier_ids: list) -> dict:
        """查询未结算红票（红蓝对冲检查）"""
        return self._post(f"{self._MATCH}/push-settlement/red-block-check", schema=LIST_DATA_RESPONSE,
                          json=list(supplier_ids))

    # ==================== 强制匹配 ====================

    def get_supplier_options(self, keyword: str = None, limit: int = 20) -> dict:
        """搜索供应商选项"""
        params = {"limit": limit}
        if keyword:
            params["keyword"] = keyword
        return self._post(f"{self._FORCE}/supplier-options", schema=LIST_DATA_RESPONSE, json=params)

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
        return self._post(f"{self._FORCE}/page-unsettled", schema=PAGE_RESPONSE, json=params)

    def load_receipt_items(self, supplier_id, receipt_nos: list = None, return_nos: list = None) -> dict:
        """读取未结算收/退货单详情（商品明细）"""
        params = {"supplierId": supplier_id}
        if receipt_nos:
            params["receiptNos"] = receipt_nos
        if return_nos:
            params["returnNos"] = return_nos
        return self._post(f"{self._FORCE}/load-receipt-items", schema=OBJECT_DATA_RESPONSE, json=params)

    def check_invoice_summary(self, supplier_id, invoice_nos: list) -> dict:
        """校验发票信息（冲突检查）"""
        return self._post(f"{self._FORCE}/invoice-summary", schema=OBJECT_DATA_RESPONSE, json={
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
        return self._post(f"{self._FORCE}/submit", schema=OBJECT_DATA_RESPONSE, json=params)

    def get_force_result(self, force_batch_no) -> dict:
        """查看强制匹配结果"""
        return self._get(f"{self._FORCE}/result/{force_batch_no}", schema=OBJECT_DATA_RESPONSE)

    # ==================== 操作记录 ====================

    def page_records(self, business_id, supplier_id=None, business_type: int = None,
                     page_num: int = 1, page_size: int = 10, sort: str = "DESC") -> dict:
        """分页查询操作记录"""
        params = {"businessId": business_id, "pageNum": page_num, "pageSize": page_size, "sort": sort}
        if supplier_id:
            params["supplierId"] = supplier_id
        if business_type is not None:
            params["businessType"] = business_type
        return self._post(f"{self._RECORD}/page", schema=PAGE_RESPONSE, json=params)
