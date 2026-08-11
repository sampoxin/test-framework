"""
小程序 UI 测试基类

所有小程序 UI 测试类应继承 MiniAppBase，自动获得：
- setUpClass: 每个测试类开始前 re_launch 回到首页（登录态保留）
"""
import minium
from utils.logger import logger


class MiniAppBase(minium.MiniTest):
    """小程序 UI 测试基类"""

    @classmethod
    def setUpClass(cls):
        """类初始化：先执行父类连接初始化，再 relaunch 回到首页"""
        super().setUpClass()
        logger.info(f"===== 测试类 {cls.__name__} 开始，回到首页 =====")
        cls.app.relaunch("/pages/home/index")
