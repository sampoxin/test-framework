import json
import os
import re
from typing import Dict, List, Any
from .templates import TestCaseTemplate


class APITestGenerator:
    def __init__(self, project_dir: str = None):
        self.project_dir = project_dir or os.getcwd()
        self.test_data_path = os.path.join(self.project_dir, "data", "test_data.json")
        self.testcases_dir = os.path.join(self.project_dir, "testcases")
        os.makedirs(self.testcases_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.test_data_path), exist_ok=True)

    def generate_test(self, input_data: str or Dict[str, Any]) -> Dict[str, str]:
        if isinstance(input_data, str):
            api_doc = self._parse_curl(input_data)
        else:
            api_doc = input_data
        
        result = {}
        test_data = self._generate_test_data(api_doc)
        test_case = self._generate_test_case(api_doc)
        result["test_data.json"] = json.dumps(test_data, ensure_ascii=False, indent=2)
        result["test_file.py"] = test_case
        return result

    def _parse_curl(self, curl_command: str) -> Dict[str, Any]:
        method = "GET"
        url = ""
        headers = {}
        data = {}
        json_data = {}
        
        lines = curl_command.strip().split('\n')
        full_command = ' '.join([line.strip() for line in lines])
        
        if '-X' in full_command or '--request' in full_command:
            match = re.search(r'-X\s+(\w+)|--request\s+(\w+)', full_command, re.IGNORECASE)
            if match:
                method = match.group(1) or match.group(2)
        
        url_pattern = r'curl\s+(?:--location\s+)?(?:-X\s+\w+\s+|--request\s+\w+\s+)?["\']?([^\s"\']+)["\']?'
        url_match = re.search(url_pattern, full_command)
        if url_match:
            url = url_match.group(1)
        
        header_pattern = r'-H\s+["\']([^"\']+)["\']|--header\s+["\']([^"\']+)["\']'
        header_matches = re.findall(header_pattern, full_command)
        for match in header_matches:
            header = match[0] or match[1]
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
        
        data_pattern = r"--data-raw\s+('(.*?)'|\"(.*?)\")|--data\s+('(.*?)'|\"(.*?)\")|-d\s+('(.*?)'|\"(.*?)\")"
        data_matches = re.findall(data_pattern, full_command, re.DOTALL)
        for match in data_matches:
            data_str = match[1] or match[2] or match[3] or match[4] or match[5] or match[6]
            if data_str:
                try:
                    json_data = json.loads(data_str)
                except json.JSONDecodeError:
                    pairs = data_str.split('&')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            data[key] = value
        
        if headers.get('Content-Type') == 'application/json' and not json_data and data:
            json_data = data
        
        required_params = []
        optional_params = []
        param_types = {}
        param_values = {}
        
        if json_data:
            required_params = list(json_data.keys())
            for key, value in json_data.items():
                param_types[key] = self._detect_type(value)
                param_values[key] = value
        
        module_name = self._extract_module_name(url)
        api_name = self._extract_api_name(url)
        
        return {
            "epic": f"{self._translate_to_chinese(module_name)}模块",
            "feature": f"{self._translate_to_chinese(module_name)}功能",
            "module": module_name,
            "apis": [{
                "name": api_name,
                "method": method,
                "path": self._extract_path_after_com(url),
                "full_path": url,
                "description": f"{method} {url}",
                "required_params": required_params,
                "optional_params": optional_params,
                "param_types": param_types,
                "param_values": param_values,
                "success_response": {"code": "Success"},
                "error_codes": ["FAIL"]
            }]
        }

    def _extract_module_name(self, url):
        parts = url.strip('/').split('/')
        if len(parts) >= 3:
            return parts[-2]
        return "api"

    def _extract_path_after_com(self, url):
        match = re.search(r'com(/.*)', url)
        if match:
            return match.group(1)
        return url

    def _translate_to_chinese(self, name):
        mappings = {
            "coupon": "优惠券", "member": "会员", "user": "用户", "order": "订单",
            "product": "商品", "address": "地址", "activity": "活动", "payment": "支付",
            "marketing": "营销", "report": "报告", "config": "配置", "setting": "设置",
            "message": "消息", "notification": "通知", "sms": "短信", "email": "邮件",
            "login": "登录", "register": "注册", "logout": "退出", "profile": "资料",
            "list": "列表", "detail": "详情", "create": "创建", "update": "更新",
            "delete": "删除", "search": "搜索", "export": "导出", "import": "导入",
            "sync": "同步", "audit": "审核", "approve": "审批", "generate": "生成",
            "api": "接口"
        }
        return mappings.get(name.lower(), name)

    def _detect_type(self, value):
        if isinstance(value, int):
            return "int"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, str):
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return "date"
            elif re.match(r'^1[3-9]\d{9}$', value):
                return "phone"
            return "string"
        else:
            return "string"

    def _extract_api_name(self, url):
        parts = url.strip('/').split('/')
        if len(parts) >= 2:
            return f"{parts[-2]}_{parts[-1]}"
        return "api_request"

    def _generate_test_data(self, api_doc: Dict[str, Any]) -> Dict[str, List[Dict]]:
        test_data = {}
        for api in api_doc.get("apis", []):
            data_key = self._get_data_key(api["name"])
            test_data[data_key] = self._generate_api_test_cases(api)
        existing_data = self._load_existing_data()
        for key, value in test_data.items():
            if key not in existing_data:
                existing_data[key] = value
            else:
                print(f"警告：测试数据键 '{key}' 已存在，跳过追加")
        return existing_data

    def _generate_api_test_cases(self, api: Dict[str, Any]) -> List[Dict]:
        cases = []
        method = api["method"].upper()
        required_params = api.get("required_params", [])
        optional_params = api.get("optional_params", [])
        param_types = api.get("param_types", {})
        param_values = api.get("param_values", {})

        cases.append({
            "case_name": f"{api['name']}-正常请求",
            "request_data": {**self._generate_valid_params(required_params, param_types, param_values),
                           **self._generate_valid_params(optional_params, param_types, param_values)},
            "expected_code": "Success",
            "mark": "p0"
        })

        for param in required_params:
            cases.append({
                "case_name": f"{api['name']}-缺少{param}",
                "request_data": {**self._generate_valid_params([p for p in required_params if p != param], param_types, param_values),
                               **self._generate_valid_params(optional_params, param_types, param_values)},
                "expected_code": "FAIL",
                "mark": "p3"
            })
            cases.append({
                "case_name": f"{api['name']}-{param}为空",
                "request_data": {**self._generate_valid_params(required_params, param_types, param_values),
                               **self._generate_valid_params(optional_params, param_types, param_values),
                               param: ""},
                "expected_code": "FAIL",
                "mark": "p3"
            })
            if param_types.get(param) == "int" and param not in ["pageNum", "pageSize"]:
                cases.append({
                    "case_name": f"{api['name']}-{param}为负数",
                    "request_data": {**self._generate_valid_params(required_params, param_types, param_values),
                                   **self._generate_valid_params(optional_params, param_types, param_values),
                                   param: -1},
                    "expected_code": "FAIL",
                    "mark": "p3"
                })

        for param in optional_params:
            cases.append({
                "case_name": f"{api['name']}-可选{param}",
                "request_data": {**self._generate_valid_params(required_params, param_types, param_values),
                               **self._generate_valid_params(optional_params, param_types, param_values),
                               param: self._generate_value_by_type(param_types.get(param, "string"), param, param_values.get(param, ""))},
                "expected_code": "Success",
                "mark": "p2"
            })

        return cases

    def _generate_valid_params(self, params: List[str], param_types: Dict, param_values: Dict) -> Dict[str, Any]:
        result = {}
        for param in params:
            result[param] = self._generate_value_by_type(param_types.get(param, "string"), param, param_values.get(param, ""))
        return result

    def _generate_value_by_type(self, param_type: str, param_name: str = "", param_value: Any = "") -> Any:
        if param_name == "sort":
            return "ASC"
        elif param_name == "pageNum":
            return 1
        elif param_name == "pageSize":
            return 10
        elif param_name == "status":
            if param_value:
                param_value_str = str(param_value)
                enum_values = re.findall(r'(\d+)-', param_value_str)
                if enum_values:
                    return enum_values[0]
                return param_value
        
        param_type = param_type.lower()
        if param_type in ["string", "str"]:
            return "DYNAMIC_text_10"
        elif param_type in ["int", "integer"]:
            return 1
        elif param_type in ["bool", "boolean"]:
            return True
        elif param_type in ["date", "datetime"]:
            return "2024-01-01"
        elif param_type in ["phone", "mobile"]:
            return "DYNAMIC_phone"
        elif param_type in ["name"]:
            return "DYNAMIC_name"
        else:
            return "test_value"

    def _generate_test_case(self, api_doc: Dict[str, Any]) -> str:
        template = TestCaseTemplate()
        return template.generate(api_doc)

    def _get_data_key(self, api_name: str) -> str:
        english_name = self._translate_to_english(api_name)
        return english_name.lower().replace(" ", "_").replace("api", "").replace("-", "_").strip("_")

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
            "通知": "_notify_", "消息": "_message_", "短信": "_sms_", "邮件": "_email_"
        }
        result = name
        for chinese, english in mappings.items():
            result = result.replace(chinese, english)
        return result.replace("__", "_").strip("_")

    def _load_existing_data(self) -> Dict:
        if os.path.exists(self.test_data_path):
            with open(self.test_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_files(self, input_data: str or Dict[str, Any]) -> None:
        result = self.generate_test(input_data)
        with open(self.test_data_path, "w", encoding="utf-8") as f:
            f.write(result["test_data.json"])
        
        if isinstance(input_data, str):
            api_doc = self._parse_curl(input_data)
        else:
            api_doc = input_data
        
        module_name = api_doc.get("module", "api")
        test_file_name = f"test_{module_name}.py"
        test_file_path = os.path.join(self.testcases_dir, test_file_name)
        
        if os.path.exists(test_file_path):
            self._append_test_method(test_file_path, api_doc)
            print(f"测试用例已追加到: {test_file_path}")
        else:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(result["test_file.py"])
            print(f"测试用例已保存: {test_file_path}")
        
        print(f"测试数据已保存: {self.test_data_path}")

    def _append_test_method(self, file_path: str, api_doc: dict) -> None:
        template = TestCaseTemplate()
        apis = api_doc.get("apis", [])
        new_methods = []
        
        for api in apis:
            data_key = self._get_data_key(api["name"])
            method_name = data_key
            new_methods.append(template._generate_method(api, method_name, data_key))
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        class_pattern = r'(class Test\w+:\s*)$'
        match = re.search(class_pattern, content, re.MULTILINE)
        if match:
            insert_pos = match.end()
            indent = '    '
            new_content = content[:insert_pos] + '\n' + '\n'.join([indent + method for method in new_methods]) + '\n' + content[insert_pos:]
        else:
            new_content = content + '\n\n' + '\n'.join(new_methods)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)