# run_flet.py - 最小可运行版本（无事件）
from pathlib import Path
import sys
import flet as ft

sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage

def main(page: ft.Page):
    """主入口 - 只测试UI和路由"""
    print("🚀 应用启动（无事件绑定）")
    
    # 基础窗口配置
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    page.window_min_width = 600
    page.window_min_height = 500
    
    # 创建路由
    router = BaseRouter(page)
    
    # ========== 只创建页面，不注册任何事件 ==========
    
    # 关键：实例化后立即build，让组件存在
    home_page = HomePage(None, page)
    print(f"📦 HomePage 组件: {list(home_page.components.keys())}")
    
    generator_page = GeneratorPage(None, page)
    print(f"📦 GeneratorPage 组件: {list(generator_page.components.keys())}")
    
    localizer_page = LocalizerPage(None, page)
    print(f"📦 LocalizerPage 组件: {list(localizer_page.components.keys())}")
    
    settings_page = SettingsPage(None, page)
    print(f"📦 SettingsPage 组件: {list(settings_page.components.keys())}")
    
    # 注册到路由（用lambda包装builder，延迟执行）
    router.add_route("home", "首页", ft.icons.HOME, lambda: home_page.build())
    router.add_route("generator", "生成器", ft.icons.BUILD, lambda: generator_page.build())
    router.add_route("localizer", "本地化", ft.icons.LANGUAGE, lambda: localizer_page.build())
    router.add_route("settings", "设置", ft.icons.SETTINGS, lambda: settings_page.build())
    
    # 显示首页
    print("📍 显示首页...")
    router.go("home")
    
    print("✅ 启动完成，现在可以测试路由切换")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)  # 显示控制台