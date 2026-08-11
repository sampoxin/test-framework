"""
企业微信机器人通知工具

使用方法：
1. 在企业微信群中创建群机器人
2. 获取 Webhook 地址（形如 https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx）
3. 配置环境变量 WECOM_WEBHOOK
"""

import requests
import json
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger()


class WeComNotifier:
    """企业微信机器人通知器"""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)

    def send_text(self, content: str, mentioned_list: Optional[list] = None,
                  mentioned_mobile_list: Optional[list] = None) -> bool:
        """
        发送文本消息

        Args:
            content: 消息内容
            mentioned_list: @userid 列表，如 ["wangqing","@all"] 表示@所有人
            mentioned_mobile_list: @手机号 列表
        """
        if not self.enabled:
            logger.warning("企业微信未配置，跳过通知")
            return False

        message: Dict = {
            "msgtype": "text",
            "text": {"content": content}
        }
        if mentioned_list:
            message["text"]["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            message["text"]["mentioned_mobile_list"] = mentioned_mobile_list

        return self._send(message)

    def send_markdown(self, content: str) -> bool:
        """
        发送 Markdown 消息

        企业微信 Markdown 支持：
        - **加粗**、> 引用、`代码`、<font color="info/comment/warning">文字</font>
        - [链接](url)、![图片](url)
        不支持：# 标题、--- 分隔线、表格、无序列表（- 开头）

        Args:
            content: Markdown 内容
        """
        if not self.enabled:
            logger.warning("企业微信未配置，跳过通知")
            return False

        message = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }
        return self._send(message)

    def send_test_report(self, test_result: Dict) -> bool:
        """
        发送测试报告（4块结构，适配企业微信 Markdown）

        Args:
            test_result: 测试结果字典，字段同钉钉通知
        """
        if not self.enabled:
            logger.warning("企业微信未配置，跳过通知")
            return False

        report_title = test_result.get("title", "自动化测试")
        passed = test_result.get("passed", 0)
        failed = test_result.get("failed", 0)
        skipped = test_result.get("skipped", 0)
        total = test_result.get("total", 0)
        duration = test_result.get("duration", 0)
        env = test_result.get("env", "unknown")
        modules = test_result.get("modules", {})
        failed_cases = test_result.get("failed_cases", [])

        success_rate = (passed / total * 100) if total > 0 else 0
        # 整体结果颜色
        color = "info" if failed == 0 else "warning"
        status = "✅ 通过" if failed == 0 else "❌ 失败"

        # 耗时格式化
        if duration >= 60:
            duration_str = f"{int(duration // 60)}分{duration % 60:.0f}秒"
        else:
            duration_str = f"{duration:.1f}秒"

        # 第1块：标题
        lines = [
            f"**📊 {report_title}**",
            f"> 环境：<font color=\"info\">{env}</font> 结果：<font color=\"{color}\">{status}</font>",
            "",
        ]

        # 第2块：指标
        lines += [
            "**📈 执行指标**",
            f"> 总用例：<font color=\"info\">{total}</font>",
            f"> ✅ 成功：<font color=\"info\">{passed}</font>",
            f"> ❌ 失败：<font color=\"warning\">{failed}</font>",
            f"> ⏭ 跳过：<font color=\"comment\">{skipped}</font>",
            f"> 📊 通过率：<font color=\"{color}\">{success_rate:.1f}%</font>",
            f"> ⏱ 耗时：<font color=\"info\">{duration_str}</font>",
            "",
        ]

        # 第3块：模块统计
        if modules:
            lines.append("**🗂 模块统计**")
            for name, stat in modules.items():
                icon = "✅" if stat.get("failed", 0) == 0 else "❌"
                mod_color = "info" if stat.get("failed", 0) == 0 else "warning"
                lines.append(
                    f"> {icon} <font color=\"{mod_color}\">{name}</font>："
                    f"{stat.get('total', 0)}条 "
                    f"(成功{stat.get('passed', 0)} / 失败{stat.get('failed', 0)} / 跳过{stat.get('skipped', 0)})"
                )
            lines.append("")

        # 第4块：失败用例（最多显示5条）
        if failed_cases:
            lines.append("**🚨 失败用例**")
            for i, case in enumerate(failed_cases[:5], 1):
                lines.append(f"> {i}. <font color=\"warning\">{case}</font>")
            if len(failed_cases) > 5:
                lines.append(f"> 仅展示前5条，共 {len(failed_cases)} 条失败")
            lines.append("")

        lines.append(f"📅 {test_result.get('date', '')}")

        markdown_text = "\n".join(lines)

        return self.send_markdown(markdown_text)

    def _send(self, message: Dict) -> bool:
        """发送消息的内部方法"""
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get("errcode") == 0:
                logger.info("企业微信通知发送成功")
                return True
            else:
                logger.error(f"企业微信通知发送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"企业微信通知发送异常: {str(e)}")
            return False
