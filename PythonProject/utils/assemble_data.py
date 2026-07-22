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
        optional_fields = [
            "deductionAdjustAmountWithTax",
            "deductionAdjustedAmountWithTax",
            "deductionAdjustedAmountWithoutTax",
            "deductionAdjustedTaxAmount",
            "deductionAdjustedPriceWithTax",
            "deductionAdjustedPriceWithoutTax"
        ]
        for field in optional_fields:
            if field in item and item[field] is not None:
                target_item[field] = item[field]
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


_BUILTIN_DATA = [
    {"itemName": "*糖*TH&BO泰国椰子糖", "itemCode": "19021303854", "itemSpec": "108g"},
    {"itemName": "*糖*TH&BO泰国榴莲糖", "itemCode": "19021100480", "itemSpec": "108g"},
    {"itemName": "*糖*TH&BO泰国椰子糖", "itemCode": "19021303858", "itemSpec": "48g"},
    {"itemName": "*糖*TH&BO泰国榴莲糖", "itemCode": "19021303856", "itemSpec": "48g"}
]


def get_item_code(item_name, item_spec=None):
    """
    根据 itemName 和 itemSpec 匹配 itemCode
    优先级：先用 itemName 匹配 → 1条直接返回；多条再用 itemSpec 过滤 → 还多条取第一个
    :param item_name: 商品名称，例如 "*糖*TH&BO泰国椰子糖"
    :param item_spec: 商品规格，例如 "108g"，可选
    :return: 匹配的 itemCode，未找到返回 None
    """
    matched = [item for item in _BUILTIN_DATA if item["itemName"] == item_name]
    if len(matched) == 1:
        return matched[0]["itemCode"]
    if len(matched) > 1 and item_spec is not None:
        matched = [item for item in matched if item["itemSpec"] in item_spec]
    return matched[0]["itemCode"] if matched else None