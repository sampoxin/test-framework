def convert_receipt_data(source_data):
    """
    将第一个接口返回数据转换为目标数组格式
    :param source_data: 原始第一层完整json数据（dict）
    :return: 转换后的目标列表数组
    """
    result_list = []
    # 获取明细行
    receipt_items = source_data["data"]["receiptItems"]
    return_items = source_data["data"]["returnItems"]

    for item in receipt_items:
        target_item = {
            "receiptNo": item["receiptOrReturnNo"],
            "receiptDetailNo": item["receiptDetailNo"],
            "receiptItemId": item["receiptItemId"],
            "itemCode": item["itemCode"],
            "itemName": item["itemName"],
            "itemSpec": item["itemSpec"],
            "unit": item["unit"],
            "orderNo": item["orderNo"],
            "taxRate": int(item["taxRate"] * 100),  # 0.13 -> 13
            "receiptDate": item["receiptDate"],
            "matchQty": item["unmatchedQty"],
            "priceWithTax": item["priceWithTax"],
            "priceWithoutTax": item["priceWithoutTax"],
            "matchAmountWithTax": item["unmatchedAmountWithTax"],
            "matchAmountWithoutTax": item["unmatchedAmountWithoutTax"],
            "matchTaxAmount": item["unmatchedTaxAmount"],
            "userAdjusted": False,
            "deleted": False
        }
        result_list.append(target_item)

    for item in return_items:
        target_item = {
            "returnNo": item["receiptOrReturnNo"],
            "receiptDetailNo": item["receiptDetailNo"],
            "receiptItemId": item["receiptItemId"],
            "itemCode": item["itemCode"],
            "itemName": item["itemName"],
            "itemSpec": item["itemSpec"],
            "unit": item["unit"],
            "orderNo": item["orderNo"],
            "taxRate": int(item["taxRate"] * 100),  # 0.13 -> 13
            "receiptDate": item["receiptDate"],
            "matchQty": item["unmatchedQty"],
            "priceWithTax": item["priceWithTax"],
            "priceWithoutTax": item["priceWithoutTax"],
            "matchAmountWithTax": item["unmatchedAmountWithTax"],
            "matchAmountWithoutTax": item["unmatchedAmountWithoutTax"],
            "matchTaxAmount": item["unmatchedTaxAmount"],
            "userAdjusted": False,
            "deleted": False
        }
        result_list.append(target_item)

    return result_list
