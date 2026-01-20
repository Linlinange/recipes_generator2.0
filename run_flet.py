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
    """主入口 - 手动调用build()，不修改底层"""
    print("=" * 60)
    print("🚀 应用启动")
    print("=" * 60)
    
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    
    # 创建Router
    router = BaseRouter(page)
    
    # ========== 关键修复：实例化后立即build() ==========
    
    print("[1] 创建并构建页面...")
    
    home_page = HomePage(None, page)
    home_content = home_page.build()  # ✅ 手动调用
    print(f"  → HomePage: {len(home_page.components)} 个组件")
    
    generator_page = GeneratorPage(None, page)
    generator_content = generator_page.build()  # ✅ 手动调用
    print(f"  → GeneratorPage: {len(generator_page.components)} 个组件")
    
    localizer_page = LocalizerPage(None, page)
    localizer_content = localizer_page.build()  # ✅ 手动调用
    print(f"  → LocalizerPage: {len(localizer_page.components)} 个组件")
    
    settings_page = SettingsPage(None, page)
    settings_content = settings_page.build()  # ✅ 手动调用
    print(f"  → SettingsPage: {len(settings_page.components)} 个组件")
    
    print("[2] 注册路由...")
    # 注意：传 content，不再传 build 方法
    router.add_route("home", "首页", ft.icons.HOME, lambda: home_content)
    router.add_route("generator", "生成器", ft.icons.BUILD, lambda: generator_content)
    router.add_route("localizer", "本地化", ft.icons.LANGUAGE, lambda: localizer_content)
    router.add_route("settings", "设置", ft.icons.SETTINGS, lambda: settings_content)
    
    print("[3] 显示首页...")
    router.go("home")
    print("✅ 启动完成！")
    
    # ========== 从这里开始逐步添加事件 ==========
    # 下一版本再添加事件注册

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)  # 显示控制台