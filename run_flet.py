
from pathlib import Path
import sys
import flet as ft

sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_router import BaseRouter
from src.interfaces.generator_page import create_home_page, create_generator_page, create_settings_page

def main(page: ft.Page):
    """主入口"""
    # 窗口配置
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    page.window_min_width = 600
    page.window_min_height = 500
    
    # 创建路由
    router = BaseRouter(page)
    
    # 注册页面
    router.add_route(
        "home",
        "首页",
        ft.icons.HOME,
        lambda: create_home_page(router)
    )
    
    router.add_route(
        "recipe_generator",
        "配方生成器",
        ft.icons.BUILD,
        lambda: create_generator_page(router)
    )
    
    router.add_route(
        "localizer",
        "本地化生成器",
        ft.icons.BUILD,
        lambda: create_generator_page(router)
    )
    
    router.add_route(
        "settings",
        "设置",
        ft.icons.SETTINGS,
        lambda: create_settings_page(router)
    )
    
    # 默认显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)