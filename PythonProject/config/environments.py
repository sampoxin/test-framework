"""
==========================================
  配置文件 - 简化版
==========================================

这个文件包含所有的配置信息！
通过环境变量切换不同的配置。

【使用方法】

1. 切换到开发环境：
   import os
   os.environ["LOCUST_ENV"] = "dev"

2. 切换到测试环境：
   os.environ["LOCUST_ENV"] = "test"

3. 查看当前配置：
   from config import show_config
   show_config()

4. 获取配置项：
   from config import BASE_URL, QUESTIONNAIRE_ID
   print(f"API地址：{BASE_URL}")
   print(f"问卷ID：{QUESTIONNAIRE_ID}")
"""

import os


# ==========================================
# 第1部分：定义所有环境
# ==========================================

class Environment:
    """环境枚举"""
    DEV = "dev"      # 开发环境
    TEST = "test"     # 测试环境
    PRE = "pre"       # 预发环境
    PROD = "prod"    # 生产环境


# ==========================================
# 第2部分：定义所有环境的配置
# ==========================================

# 每个环境的配置项
ENVIRONMENTS = {
    # ---------- 开发环境 ----------
    Environment.DEV: {
        "name": "开发环境",
        "base_url": "https://dev-ocss-gateway.youdtj.com",
        "admin_url": "https://dev-ocss.youdtj.com",
        "questionnaire_id": 590,
        "activity_id": 471,
        "timeout": 30,
        "tenant": "9999",
        "db": {
            "host": os.environ.get("DB_HOST", ""),
            "port": int(os.environ.get("DB_PORT", 3306)),
            "user": os.environ.get("DB_USER", ""),
            "password": os.environ.get("DB_PASSWORD", ""),
            "database": os.environ.get("DB_NAME", "mall_dev")
        }
    },
    
    # ---------- 测试环境 ----------
    Environment.TEST: {
        "name": "测试环境",
        "base_url": "https://dev-ocss-gateway.youdtj.com",
        "admin_url": "https://dev-ocss.youdtj.com",
        "questionnaire_id": 582,
        "activity_id": 100,
        "timeout": 30,
        "tenant": "1",
        "db": {
            "host": os.environ.get("TEST_DB_HOST", "192.168.1.100"),
            "port": int(os.environ.get("TEST_DB_PORT", 3306)),
            "user": os.environ.get("TEST_DB_USER", "root"),
            "password": os.environ.get("TEST_DB_PASSWORD", ""),
            "database": os.environ.get("TEST_DB_NAME", "srm")
        }
    },
    
    # ---------- 预发环境 ----------
    Environment.PRE: {
        "name": "预发环境",
        "base_url": "https://pre-ocss-gateway.youdtj.com",
        "admin_url": "https://pre-admin.youdtj.com",
        "questionnaire_id": 582,
        "activity_id": 100,
        "timeout": 20,
        "tenant": "1"
    },
    
    # ---------- 生产环境 ----------
    Environment.PROD: {
        "name": "生产环境",
        "base_url": "https://prod-ocss-gateway.youdtj.com",
        "admin_url": "https://admin.youdtj.com",
        "questionnaire_id": 582,
        "activity_id": 100,
        "timeout": 15,
        "tenant": "1"
    }
}


# ==========================================
# 第3部分：配置管理器
# ==========================================

class ConfigManager:
    """配置管理器 - 负责读取和切换配置"""
    
    def __init__(self):
        """初始化时自动读取环境变量，确定当前环境"""
        self._current_env = self._get_env_from_system()
        self._current_config = ENVIRONMENTS[self._current_env]
    
    def _get_env_from_system(self):
        """
        从系统环境变量中获取当前环境
        如果没设置，默认使用 dev（开发环境）
        """
        env_name = os.environ.get("LOCUST_ENV", "dev").lower()
        
        # 环境名称映射（支持多种写法）
        env_mapping = {
            "dev": Environment.DEV,
            "development": Environment.DEV,
            "test": Environment.TEST,
            "testing": Environment.TEST,
            "pre": Environment.PRE,
            "prepub": Environment.PRE,
            "prod": Environment.PROD,
            "production": Environment.PROD
        }
        
        # 返回对应的环境，默认开发环境
        return env_mapping.get(env_name, Environment.DEV)
    
    def switch_env(self, env_name):
        """切换环境"""
        env_mapping = {
            "dev": Environment.DEV,
            "test": Environment.TEST,
            "pre": Environment.PRE,
            "prod": Environment.PROD
        }
        
        new_env = env_mapping.get(env_name.lower(), Environment.DEV)
        self._current_env = new_env
        self._current_config = ENVIRONMENTS[new_env]
        
        print(f"[切换] 环境已切换至: {self._current_config['name']}")


# ==========================================
# 第4部分：创建全局配置实例
# ==========================================

# 创建一个全局的配置管理器（整个程序只有一个）
config = ConfigManager()


# ==========================================
# 第5部分：便捷访问函数
# ==========================================

def get_config():
    """获取当前配置（字典格式）"""
    return config._current_config


def get_env():
    """获取当前环境代码"""
    return config._current_env


def show_config():
    """
    显示当前配置
    使用方法：from config import show_config; show_config()
    """
    cfg = config._current_config
    
    print("\n" + "=" * 50)
    print("[配置] 当前配置信息")
    print("=" * 50)
    print(f"环境名称：{cfg['name']}")
    print(f"环境代码：{config._current_env}")
    print(f"API地址：{cfg['base_url']}")
    print(f"问卷ID：{cfg['questionnaire_id']}")
    print(f"活动ID：{cfg['activity_id']}")
    print(f"超时时间：{cfg['timeout']} 秒")
    print(f"租户ID：{cfg['tenant']}")
    print("=" * 50 + "\n")


def list_envs():
    """
    列出所有可用环境
    使用方法：from config import list_envs; list_envs()
    """
    print("\n[环境] 可用环境列表：")
    print("-" * 50)
    for env, cfg in ENVIRONMENTS.items():
        print(f"  {env:10} - {cfg['name']} ({cfg['base_url']})")
    print("-" * 50 + "\n")
