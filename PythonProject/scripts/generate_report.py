import os
import sys
import time
import shutil
import subprocess
from datetime import datetime


def generate_report(test_script, host, users=10, rate=2, duration="30s"):
    """
    生成Locust性能测试报告
    
    参数:
        test_script: 测试脚本路径
        host: 测试目标主机
        users: 并发用户数
        rate: 每秒启动用户数
        duration: 测试时长
    """
    # 创建时间戳目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = f"reports/locust-report/{timestamp}"
    os.makedirs(report_dir, exist_ok=True)
    
    print(f"📁 创建报告目录: {report_dir}")
    
    # 运行Locust测试
    html_report = f"{report_dir}/report.html"
    csv_prefix = f"{report_dir}/stats"
    
    cmd = [
        "locust", "-f", test_script,
        "--host", host,
        "--html", html_report,
        "--csv", csv_prefix,
        "--headless",
        "-u", str(users),
        "-r", str(rate),
        "-t", duration
    ]
    
    print(f"🚀 运行测试命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0 and result.returncode != 2:
            print(f"❌ 测试运行失败: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return None
    
    # 读取统计数据生成Markdown报告
    generate_markdown_report(report_dir)
    
    # 清理不必要的CSV文件，只保留必要的报告
    clean_unnecessary_files(report_dir)
    
    # 更新latest软链接（Windows使用快捷方式）
    update_latest_link(report_dir)
    
    print(f"✅ 报告生成完成: {report_dir}")
    return report_dir


def generate_markdown_report(report_dir):
    """生成Markdown分析报告"""
    stats_file = f"{report_dir}/stats_stats.csv"
    
    if not os.path.exists(stats_file):
        print("⚠️ 统计文件不存在，跳过Markdown生成")
        return
    
    # 读取CSV数据
    with open(stats_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    headers = lines[0].strip().split(',')
    data = []
    for line in lines[1:]:
        if line.strip():
            data.append(line.strip().split(','))
    
    # 提取聚合数据
    aggregated = None
    api_data = []
    for row in data:
        if row[1] == 'Aggregated':
            aggregated = row
        else:
            api_data.append(row)
    
    # 生成Markdown内容
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""# 性能测试报告

## 📊 测试概览

| 属性 | 值 |
|------|-----|
| 测试时间 | {now} |
| 报告目录 | {os.path.basename(report_dir)} |
| 总请求数 | {aggregated[2]} |
| 失败请求 | {aggregated[3]} |
| 失败率 | {float(aggregated[3])/float(aggregated[2])*100:.2f}% |
| 平均响应时间 | {float(aggregated[5]):.2f} ms |
| 中位数响应时间 | {aggregated[4]} ms |
| 每秒请求数 | {float(aggregated[9]):.2f} |

## 📈 各接口性能

| 接口 | 请求数 | 平均响应(ms) | P90(ms) | P99(ms) |
|------|--------|--------------|----------|----------|
"""
    
    for row in api_data:
        md_content += f"| {row[1].split('/')[-1]} | {row[2]} | {float(row[5]):.2f} | {row[14]} | {row[17]} |\n"
    
    md_content += """

## ⚠️ 性能警告

以下接口响应时间超过500ms，建议优化：

| 接口 | 平均响应时间 | 状态 |
|------|--------------|------|
"""
    
    slow_apis = []
    for row in api_data:
        avg_time = float(row[5])
        if avg_time > 500:
            slow_apis.append((row[1].split('/')[-1], avg_time))
    
    if slow_apis:
        for api, time_ms in slow_apis:
            md_content += f"| {api} | {time_ms:.2f} ms | ❌ 需要优化 |\n"
    else:
        md_content += "| 无 | - | ✅ 所有接口性能良好 |\n"
    
    md_content += f"""

---

*报告生成时间: {now}*
*报告位置: [{os.path.basename(report_dir)}/report.html]({os.path.basename(report_dir)}/report.html)*
"""
    
    with open(f"{report_dir}/report.md", 'w', encoding='utf-8') as f:
        f.write(md_content)


def clean_unnecessary_files(report_dir):
    """清理不必要的CSV文件"""
    files_to_keep = {'report.html', 'report.md', 'stats_stats.csv'}
    
    for filename in os.listdir(report_dir):
        if filename not in files_to_keep:
            filepath = os.path.join(report_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(f"🗑️ 清理文件: {filename}")


def update_latest_link(report_dir):
    """更新latest标记文件"""
    latest_file = "reports/locust-report/latest.txt"
    
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(os.path.basename(report_dir))
    
    print(f"🔗 更新latest标记: {os.path.basename(report_dir)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_report.py <测试脚本> [主机] [用户数] [速率] [时长]")
        sys.exit(1)
    
    test_script = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8080"
    users = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    rate = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    duration = sys.argv[5] if len(sys.argv) > 5 else "30s"
    
    result = generate_report(test_script, host, users, rate, duration)
    
    if result:
        print(f"\n🎉 报告已生成：")
        print(f"   HTML报告: {result}/report.html")
        print(f"   MD报告: {result}/report.md")
        print(f"\n📋 报告摘要:")
        with open(f"{result}/report.md", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:25]:
                print(line, end='')