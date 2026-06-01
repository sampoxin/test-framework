import json


class TestCaseTemplate:
    def generate(self, api_doc: dict) -> str:
        epic = api_doc.get("epic", "默认模块")
        feature = api_doc.get("feature", "默认功能")
        module = api_doc.get("module", "api")
        apis = api_doc.get("apis", [])
        imports = self._generate_imports()
        class_def = self._generate_class_def(epic, feature, module)
        test_methods = self._generate_test_methods(apis)
        return f"{imports}\n\n{TEST_DATA}\n\n{class_def}\n{test_methods}\n"

    def _generate_imports(self) -> str:
        return """import allure
import pytest
from utils.tools import load_test_data, resolve_dynamic_fields"""

    def _generate_class_def(self, epic: str, feature: str, module: str) -> str:
        return f'''@allure.epic("{epic}")
@allure.feature("{feature}")
class Test{self._to_camel_case(module)}:'''

    def _generate_test_methods(self, apis: list) -> str:
        methods = []
        for api in apis:
            data_key = self._get_data_key(api["name"])
            method_name = data_key
            methods.append(self._generate_method(api, method_name, data_key))
        return "\n".join(methods)
    
    def _get_data_key(self, api_name: str) -> str:
        english_name = self._translate_to_english(api_name)
        return english_name.lower().replace(" ", "_").replace("api", "").replace("-", "_").strip("_")

    def _generate_method(self, api: dict, method_name: str, data_key: str) -> str:
        name = api["name"]
        method = api["method"].upper()
        path = api["path"]
        required_params = api.get("required_params", [])
        optional_params = api.get("optional_params", [])
        has_params = len(required_params) > 0 or len(optional_params) > 0

        if has_params:
            return self._generate_parametrized_method(name, method, path, method_name, data_key)
        else:
            return self._generate_simple_method(name, method, path, method_name)

    def _generate_simple_method(self, name: str, method: str, path: str, method_name: str) -> str:
        return f'''    @allure.story("{name}")
    @pytest.mark.p0
    def test_{method_name}(self, client):
        resp = client.send("{method}", "{path}")
        assert resp.json()["code"] == "Success"'''

    def _generate_parametrized_method(self, name: str, method: str, path: str, method_name: str, data_key: str) -> str:
        return f'''    @allure.story("{name}")
    @pytest.mark.parametrize("data", TEST_DATA["{data_key}"], ids=[x["case_name"] for x in TEST_DATA["{data_key}"]])
    def test_{method_name}(self, client, data):
        data_fields = resolve_dynamic_fields(data["request_data"])
        resp = client.send("{method}", "{path}", json=data_fields)
        assert resp.json()["code"] == data["expected_code"]'''

    def _to_camel_case(self, s: str) -> str:
        parts = s.replace("_", " ").replace("-", " ").split()
        return "".join(part.capitalize() for part in parts)

    def _to_snake_case(self, s: str) -> str:
        return s.lower().replace(" ", "_").replace("-", "_").strip("_")

    def _translate_to_english(self, name: str) -> str:
        mappings = {
            "创建": "_create_", "查询": "_query_", "获取": "_get_", "更新": "_update_",
            "删除": "_delete_", "取消": "_cancel_", "列表": "_list_", "详情": "_detail_",
            "信息": "_info_", "订单": "_order_", "会员": "_member_", "商品": "_product_",
            "用户": "_user_", "地址": "_address_", "支付": "_pay_", "提交": "_submit_",
            "保存": "_save_", "验证": "_validate_", "登录": "_login_", "注册": "_register_",
            "退出": "_logout_", "发送": "_send_", "接收": "_receive_", "上传": "_upload_",
            "下载": "_download_", "导入": "_import_", "导出": "_export_", "搜索": "_search_",
            "统计": "_statistics_", "报告": "_report_", "配置": "_config_", "设置": "_setting_",
            "审核": "_audit_", "审批": "_approve_", "生成": "_generate_", "同步": "_sync_",
            "通知": "_notify_", "消息": "_message_", "短信": "_sms_", "邮件": "_email_",
            "模块": "_module_", "功能": "_feature_", "操作": "_operation_"
        }
        result = name
        for chinese, english in mappings.items():
            result = result.replace(chinese, english)
        return result.replace("__", "_").strip("_")


TEST_DATA = """TEST_DATA = load_test_data("test_data.json")"""