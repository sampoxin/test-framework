"""
文件操作工具
用于测试执行过程中数据的读写
"""
import os
import json
import csv
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger()

# 默认输出目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'output')


class FileHelper:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or DATA_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_filepath(self, filename):
        """获取文件完整路径，文件名自动拼接日期前缀（如 2026-07-09-test.json）"""
        if os.path.isabs(filename):
            return filename
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_prefix}-{filename}"
        return os.path.join(self.output_dir, filename)

    def write_json(self, data, filename):
        """写入JSON文件（覆盖）"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        logger.info(f"[文件] JSON写入完成: {filepath}")
        return filepath

    def append_json(self, data, filename):
        """追加写入JSONL文件（每行一个JSON对象），无需读取全文件"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write('\n'+json.dumps(data, ensure_ascii=False))
        logger.info(f"[文件] JSON追加完成: {filepath}")
        return filepath

    def write_text(self, content, filename, mode='w'):
        """写入文本文件"""
        filepath = self._get_filepath(filename)
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
        logger.info(f"[文件] 文本写入完成: {filepath}")
        return filepath

    def append_text(self, content, filename):
        """追加写入文本文件"""
        return self.write_text(content + '\n', filename, mode='a')

    def write_csv(self, rows, filename, headers=None):
        """写入CSV文件"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            writer.writerows(rows)
        logger.info(f"[文件] CSV写入完成: {filepath}")
        return filepath

    def append_csv(self, row, filename):
        """追加一行到CSV文件"""
        filepath = self._get_filepath(filename)
        file_exists = os.path.exists(filepath)
        with open(filepath, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        logger.info(f"[文件] CSV追加完成: {filepath}")
        return filepath

    def read_json(self, filename):
        """读取JSON文件"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"[文件] JSON读取完成: {filepath}")
        return data

    def read_jsonl(self, filename):
        """读取JSONL文件，返回对象列表"""
        filepath = self._get_filepath(filename)
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        logger.info(f"[文件] JSONL读取完成: {filepath}, 共{len(data)}条")
        return data

    def read_text(self, filename):
        """读取文本文件"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"[文件] 文本读取完成: {filepath}")
        return content

    def read_csv(self, filename):
        """读取CSV文件，返回列表"""
        filepath = self._get_filepath(filename)
        with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            return list(reader)

    def get_timestamped_filename(self, prefix='output', ext='json'):
        """生成带时间戳的文件名"""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{ts}.{ext}"

if __name__ == '__main__':
    fh = FileHelper()
    fh.write_json({'a': 1}, 'test.json')
    fh.append_json({'b': 2}, 'test.json')
