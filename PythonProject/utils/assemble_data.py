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
    {"itemName": "*糖*TH&BO泰国榴莲糖", "itemCode": "19021303856", "itemSpec": "48g"},
    {"itemName": "*焙烤食品*熟半点开心果抹茶脆饼干120g", "itemCode": "104020095", "itemSpec": "1*12"},
    {"itemName": "*焙烤食品*熟半点腰果桂花脆饼干120g", "itemCode": "104020096", "itemSpec": "1*12"},
    {"itemName": "*焙烤食品*熟半点山核桃薄脆饼干120g", "itemCode": "104020097", "itemSpec": "1*12"},
    {"itemName": "*焙烤食品*熟半点黑芝麻可可脆饼干120g", "itemCode": "104020098", "itemSpec": "1*12"},
    {"itemName": "*焙烤食品*熟半点碧根果伯爵茶脆饼干120g", "itemCode": "104020099", "itemSpec": "1*12"},
    {"itemName": "*焙烤食品*熟半点夏威夷果可可脆饼干120g", "itemCode": "104020100", "itemSpec": "1*12"},
    {"itemName": "*熟肉制品*定王台常德酱板鱼300g", "itemCode": "13100501008", "itemSpec": "1*50"},
    {"itemName": "*其他食品*杨家殿紫苏酸枣果308g", "itemCode": "13190100082", "itemSpec": "308g*20包"},
    {"itemName": "*其他食品*定王台芝麻豆子茶308g", "itemCode": "13190100083", "itemSpec": "308g*20包"},
    {"itemName": "*熟肉制品*定王台酱板鸭326g", "itemCode": "13190100022", "itemSpec": "326g*25"},
    {"itemName": "*熟肉制品*火宫殿酱板碳烤鸭300g", "itemCode": "13190100036", "itemSpec": "300g*25"},
    {"itemName": "*方便食品*白象大辣娇常规拌面方便面114g*12奶油味火鸡拌面盒装", "itemCode": "60202000980", "itemSpec": "114g*12"},
    {"itemName": "*方便食品*白象鲜面传非油炸蒸煮面方便面112.8g*5*6新疆辣皮子拌面量贩装", "itemCode": "60202000993", "itemSpec": "112.8g*5*6"},
    {"itemName": "*方便食品*白象鲜面传非油炸蒸煮面方便面116.4g*5*6川味香辣牛肉面量贩装", "itemCode": "60219002446", "itemSpec": "116.4g*5*6"},
    {"itemName": "*方便食品*白象粉面菜蛋方便面150*12金汤肥牛味桶装", "itemCode": "60219001729", "itemSpec": "150*12"},
    {"itemName": "*方便食品*白象大辣娇BIG系列方便面135g*12麻辣香锅牛肉面桶装", "itemCode": "60219000342", "itemSpec": "135*12"},
    {"itemName": "*方便食品*白象粉面菜蛋方便面166*12蒜蓉花甲味桶装", "itemCode": "60219001729", "itemSpec": "166*12"}
]


def adjust_receipt_amounts(receipt_items, target_with_tax, target_without_tax, target_tax):
    """
    将未结算明细的总金额与发票总金额对齐，差额消化到第一条明细
    :param receipt_items: convert_receipt_data() 返回的明细列表
    :param target_with_tax: 发票含税总金额
    :param target_without_tax: 发票不含税总金额
    :param target_tax: 发票税额
    :return: 调整后的明细列表
    """
    assert receipt_items, "receipt_items 为空，无法进行金额调整"
    assert all(isinstance(x, (int, float)) for x in [target_with_tax, target_without_tax, target_tax]), \
        "发票金额参数类型错误，必须是数值类型"

    current_with_tax = sum(item["matchAmountWithTax"] for item in receipt_items)
    current_without_tax = sum(item["matchAmountWithoutTax"] for item in receipt_items)
    current_tax = sum(item["matchTaxAmount"] for item in receipt_items)

    diff_with_tax = target_with_tax - current_with_tax
    diff_without_tax = target_without_tax - current_without_tax
    diff_tax = target_tax - current_tax

    first = receipt_items[0]
    first["matchAmountWithTaxBefore"] = first["matchAmountWithTax"]
    first["matchAmountWithoutTaxBefore"] = first["matchAmountWithoutTax"]
    first["matchTaxAmountBefore"] = first["matchTaxAmount"]
    first["matchAmountWithTax"] = round(first["matchAmountWithTax"] + diff_with_tax, 2)
    first["matchAmountWithoutTax"] = round(first["matchAmountWithoutTax"] + diff_without_tax, 2)
    first["matchTaxAmount"] = round(first["matchTaxAmount"] + diff_tax, 2)
    first["userAdjusted"] = True

    adjusted_with_tax = sum(item["matchAmountWithTax"] for item in receipt_items)
    adjusted_without_tax = sum(item["matchAmountWithoutTax"] for item in receipt_items)
    adjusted_tax = sum(item["matchTaxAmount"] for item in receipt_items)

    assert adjusted_with_tax==target_with_tax, (
        f"含税金额调整后仍不一致: "
        f"明细合计={round(adjusted_with_tax, 2)}, 发票金额={round(target_with_tax, 2)}, "
        f"差额={round(adjusted_with_tax - target_with_tax, 4)}"
    )
    assert adjusted_without_tax==target_without_tax, (
        f"不含税金额调整后仍不一致: "
        f"明细合计={round(adjusted_without_tax, 2)}, 发票金额={round(target_without_tax, 2)}, "
        f"差额={round(adjusted_without_tax - target_without_tax, 4)}"
    )
    assert adjusted_tax==target_tax, (
        f"税额调整后仍不一致: "
        f"明细合计={round(adjusted_tax, 2)}, 发票税额={round(target_tax, 2)}, "
        f"差额={round(adjusted_tax - target_tax, 4)}"
    )

    return receipt_items


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