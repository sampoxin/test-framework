"""
==========================================
  配置模块 - 统一导出入口
==========================================

这个文件把 environments.py 中的内容导出来，方便使用。

【使用方法】

1. 查看当前配置：
   from config import show_config
   show_config()

2. 获取配置项：
   from config import BASE_URL, QUESTIONNAIRE_ID
   print(f"API地址：{BASE_URL}")

3. 切换环境：
   import os
   os.environ["LOCUST_ENV"] = "dev"
   # 然后重新导入配置
"""

# 从 environments.py 导入所有内容
from config.environments import (
    Environment,           # 环境枚举
    ENVIRONMENTS,          # 所有环境的配置
    ConfigManager,         # 配置管理器
    config,                # 全局配置实例
    get_config,            # 获取当前配置
    get_env,               # 获取当前环境
    show_config,           # 显示配置
    list_envs              # 列出所有环境
)

# 从当前配置中提取常用配置项
_current_config = get_config()

# 导出常用配置（直接可用）
BASE_URL = _current_config["base_url"]          # API地址
QUESTIONNAIRE_ID = _current_config["questionnaire_id"]  # 问卷ID
ACTIVITY_ID = _current_config["activity_id"]    # 活动ID
TIMEOUT = _current_config["timeout"]            # 超时时间
TENANT = _current_config["tenant"]              # 租户ID

# 导出当前环境信息
CURRENT_ENV = get_env()
ENV_NAME = _current_config["name"]

# 导出所有内容
__all__ = [
    # 环境相关
    'Environment',
    'ENVIRONMENTS',
    'ConfigManager',
    'config',
    
    # 函数
    'get_config',
    'get_env',
    'show_config',
    'list_envs',
    
    # 配置项
    'BASE_URL',
    'QUESTIONNAIRE_ID',
    'ACTIVITY_ID',
    'TIMEOUT',
    'TENANT',
    'CURRENT_ENV',
    'ENV_NAME'
]
