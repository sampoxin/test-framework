import random
import json
import os
from faker import Faker
fake = Faker('zh_CN')


img = [
    "https://ocss-noprod-file.busyming.com/1/member/avatar/tmp_bf4b1ffea2919251e835a94f6c5e66283f155a16c1702974.jpg",
    "https://ocss-noprod-file.busyming.com/1/material/1772093616810_微信图片_20260212162512_127_71.jpg",
    "https://ocss-noprod-file.busyming.com/1/material/1772093273711_1770879387754_recommenderTag.png"
]

def get_img():
    return img[random.randint(0,len(img)-1)]

def load_test_data(file_name:str)->dict:
    """从JSON文件加载测试数据"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_name)
    with open(data_path, "r",encoding="utf-8") as f:
        return json.load(f)

def resolve_dynamic_fields(data):
    """解析数据中的动态字段标记"""
    resolved = {}
    for key, value in data.items():
        if isinstance(value, str) and value.startswith("DYNAMIC_"):
            resolved[key] = generate_value(value)
        else:
            resolved[key] = value
    return resolved

def generate_value(rule):
    """根据规则生成动态数据"""
    if not rule:
        return None
    rule_type = rule.split("_")[1].lower()
    if rule_type == "text":
        max_length = int(rule.split("_")[-1])
        return fake.text(max_nb_chars = max_length)
    elif rule_type == "int":
        min_int = int(rule.split("_")[2])
        max_int = int(rule.split("_")[-1])
        return random.randint(min_int, max_int)
    elif rule_type == "birthday":
        min_age = int(rule.split("_")[2])
        max_age = int(rule.split("_")[-1])
        return str(fake.date_of_birth(
            minimum_age=min_age,
            maximum_age=max_age
        ))
    elif rule_type == "phone":
        return fake.phone_number()
    elif rule_type == "name":
        return fake.name()
    elif rule_type == "avatar":
        return img[random.randint(0, len(img)-1)]
    return None

if __name__ == "__main__":
    print(resolve_dynamic_fields({"memberName":"DYNAMIC_text_10"}))
