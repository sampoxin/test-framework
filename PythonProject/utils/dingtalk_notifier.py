"""
钉钉机器人通知工具

使用方法：
1. 在钉钉群中创建自定义机器人
2. 获取 Webhook 地址和加签密钥（如果有开启加签）
3. 配置环境变量 DINGTALK_WEBHOOK 和 DINGTALK_SECRET（可选）
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger()


class DingTalkNotifier:
    """钉钉机器人通知器"""

    def __init__(self, webhook_url: Optional[str] = None, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self.enabled = bool(webhook_url)

    def _add_sign(self, url: str, secret: str) -> str:
        """为URL添加签名参数"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote(base64.b64encode(hmac_code))

        separator = '&' if '?' in url else '?'
        return f"{url}{separator}timestamp={timestamp}&sign={sign}"

    def send_text(self, content: str, at_mobiles: Optional[list] = None, is_at_all: bool = False) -> bool:
        """
        发送文本消息

        Args:
            content: 消息内容
            at_mobiles: @人的手机号列表
            is_at_all: 是否@所有人
        """
        if not self.enabled:
            logger.warning("钉钉未配置，跳过通知")
            return False

        message = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {"isAtAll": is_at_all}
        }

        if at_mobiles:
            message["at"]["atMobiles"] = at_mobiles

        return self._send(message)

    def send_markdown(self, title: str, text: str, at_mobiles: Optional[list] = None, is_at_all: bool = False) -> bool:
        """
        发送Markdown消息

        Args:
            title: 标题
            text: Markdown内容
            at_mobiles: @人的手机号列表
            is_at_all: 是否@所有人
        """
        if not self.enabled:
            logger.warning("钉钉未配置，跳过通知")
            return False

        message = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"isAtAll": is_at_all}
        }

        if at_mobiles:
            message["at"]["atMobiles"] = at_mobiles

        return self._send(message)

    def send_test_report(self, test_result: Dict) -> bool:
        """
        发送测试报告

        Args:
            test_result: 测试结果字典
                {
                    "passed": 10,
                    "failed": 2,
                    "skipped": 1,
                    "total": 13,
                    "duration": 15.5,
                    "env": "dev"
                }
        """
        if not self.enabled:
            logger.warning("钉钉未配置，跳过通知")
            return False

        passed = test_result.get("passed", 0)
        failed = test_result.get("failed", 0)
        skipped = test_result.get("skipped", 0)
        total = test_result.get("total", 0)
        duration = test_result.get("duration", 0)
        env = test_result.get("env", "unknown")

        success_rate = (passed / total * 100) if total > 0 else 0

        color = "#00FF00" if failed == 0 else "#FF0000"
        status = "✅ 通过" if failed == 0 else "❌ 失败"

        markdown_text = f"""
# 📊 自动化测试报告

> **测试环境:** {env}
> **测试状态:** {status}

---

## 📈 测试统计

| 指标 | 数值 |
|------|------|
| **总用例数** | {total} |
| **✅ 通过** | {passed} |
| **❌ 失败** | {failed} |
| **⏭️ 跳过** | {skipped} |
| **📊 通过率** | {success_rate:.1f}% |
| **⏱️ 耗时** | {duration:.1f}s |

---

📅 {test_result.get('date', '')}
        """.strip()

        return self.send_markdown(
            title=f"自动化测试报告 - {'通过' if failed == 0 else '失败'}",
            text=markdown_text,
            is_at_all=failed > 0
        )

    def _send(self, message: Dict) -> bool:
        """发送消息的内部方法"""
        try:
            url = self.webhook_url
            if self.secret:
                url = self._add_sign(url, self.secret)

            response = requests.post(
                url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get("errcode") == 0:
                logger.info("钉钉通知发送成功")
                return True
            else:
                logger.error(f"钉钉通知发送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"钉钉通知发送异常: {str(e)}")
            return False
