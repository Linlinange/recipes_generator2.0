

from pathlib import Path
import sys
import flet as ft

sys.path.append(str(Path(__file__).parent))

# 页面导入
from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage

# 服务导入（只导入已实现的核心服务）
from src.service.settings_service import SettingsService
from src.service.recipe_service import RecipeService

# ============================================================================
# 主入口 - 极简版
# ============================================================================

def main(page: ft.Page):
    """主入口 - 事件在Page内部绑定"""
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    
    # 创建单例Service
    settings_service = SettingsService()
    recipe_service = RecipeService()
    
    # 创建路由管理器
    router = BaseRouter(page)
    
    # 创建页面实例（直接注入Service）
    pages = {
        "home": HomePage(router, page),                                    # 无Service
        "generator": GeneratorPage(None, page, recipe_service),            # 注入RecipeService
        "localizer": LocalizerPage(None, page),                            # 无Service
        "settings": SettingsPage(router, page, settings_service),          # 注入SettingsService
    }
    
    # 注册路由
    route_info = {
        "home": ("首页", ft.icons.HOME),
        "generator": ("生成器", ft.icons.BUILD),
        "localizer": ("本地化", ft.icons.LANGUAGE),
        "settings": ("设置", ft.icons.SETTINGS),
    }
    
    for name, page_obj in pages.items():
        content = page_obj.build()  # build()内部已绑定所有事件
        router.add_route(name, route_info[name][0], route_info[name][1], lambda c=content: c)
    
    # 显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)