"""
后台管理系统 - 侧边栏导航组件（Ant Design Pro 菜单）
"""
from playwright.sync_api import Page
from utils.logger import logger


class Sidebar:
    """侧边栏导航组件"""

    # Ant Design 菜单选择器
    MENU_ITEM = ".ant-menu-item"                        # 叶子菜单项
    SUB_MENU_TITLE = ".ant-menu-submenu-title"          # 子菜单标题（点击展开/收起）
    SUB_MENU_OPEN = ".ant-menu-submenu-open"            # 已展开的子菜单
    SELECTED_ITEM = ".ant-menu-item-selected"           # 当前选中菜单项

    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------
    # 核心操作
    # ------------------------------------------------------------------

    def click_menu(self, name: str):
        """点击叶子菜单项（无子菜单）"""
        logger.info(f"侧边栏点击菜单: {name}")
        self.page.locator(f"{self.MENU_ITEM}:has-text('{name}')").click()
        self.page.wait_for_load_state("networkidle")
        return self

    def expand_and_click(self, parent: str, child: str, sub: str = ""):
        """
        展开父菜单并点击子菜单项
        :param parent: 一级菜单名称（展开）
        :param child:  二级菜单名称（点击）
        :param sub:    三级菜单名称（可选，点击）
        """
        logger.info(f"侧边栏展开 [{parent}] → 点击 [{child}]")
        # 展开父菜单（仅在未展开时点击）
        self._expand_parent(parent)
        # 点击二级子菜单
        self.page.locator(f"{self.MENU_ITEM}:has-text('{child}')").click()
        self.page.wait_for_load_state("networkidle")
        # 点击三级子菜单（如有）
        if sub:
            logger.info(f"侧边栏点击三级菜单: {sub}")
            self.page.locator(f"{self.MENU_ITEM}:has-text('{sub}')").click()
            self.page.wait_for_load_state("networkidle")
        return self

    def expand_menu(self, name: str):
        """只展开父菜单，不点击子项"""
        logger.info(f"侧边栏展开菜单: {name}")
        self._expand_parent(name)
        return self

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    def is_menu_active(self, name: str) -> bool:
        """指定菜单项是否处于选中（高亮）状态"""
        return self.page.locator(
            f"{self.SELECTED_ITEM}:has-text('{name}')"
        ).count() > 0

    def is_menu_visible(self) -> bool:
        """侧边栏整体是否可见"""
        return self.page.locator(".ant-layout-sider").is_visible()

    def is_expanded(self, name: str) -> bool:
        """指定父菜单是否已展开"""
        return self.page.locator(
            f"{self.SUB_MENU_OPEN}:has({self.SUB_MENU_TITLE}:has-text('{name}'))"
        ).count() > 0

    def get_all_menu_items(self) -> list[str]:
        """获取当前所有可见的菜单项文本（叶子节点）"""
        items = self.page.locator(self.MENU_ITEM).all()
        return [item.text_content().strip() for item in items if item.is_visible()]

    # ------------------------------------------------------------------
    # 私有方法
    # ------------------------------------------------------------------

    def _expand_parent(self, name: str):
        """展开指定名称的父菜单（已展开则跳过）"""
        if self.is_expanded(name):
            logger.info(f"菜单 [{name}] 已展开，跳过")
            return
        self.page.locator(f"{self.SUB_MENU_TITLE}:has-text('{name}')").click()
        self.page.wait_for_timeout(400)  # 等待 Ant Design 展开动画
