
import flet as ft
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.service.recipe_service import RecipeService

def create_home_page(router):
    """首页"""
    container = ft.Container(
        content=ft.Column([
            ft.Text("🏠 MC Recipe Generator", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("欢迎使用Minecraft配方生成工具！", size=16),
            ft.Text("功能特色：", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("• 支持批量生成JSON配方文件"),
            ft.Text("• 灵活的模板占位符替换"),
            ft.Text("• 预览模式避免误操作"),
            ft.Text("• 可视化日志输出"),
            ft.Divider(),
            ft.ElevatedButton(
                "开始使用 →",
                on_click=lambda e: router.go("generator"),
            ),
        ], spacing=20), 
        padding=20
    )

    return container

def create_generator_page(router):
    """
    生成器页面
    
    Args:
        router: BaseRouter实例，用于访问page和其他路由
        
    Returns:
        页面内容（Column）
    """
    
    # 日志显示区（弹性填充）
    log_view = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
    )
    
    # 统计信息区
    stats_container = ft.Container(
        content=ft.Text("总数: 0 个文件", size=14, weight=ft.FontWeight.BOLD),
        padding=10,
        bgcolor=ft.colors.GREY_900,
        border_radius=5,
    )
    
    # 控制面板（固定高度）
    control_panel = ft.Container(
        content=ft.Column([
            ft.Text("⚙️ 配方生成器", size=24, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                ft.Checkbox(label="预览模式", value=True),
                ft.Checkbox(label="解释模式"),
            ]),
            
            ft.Row([
                ft.ElevatedButton(
                    "🚀 开始生成",
                    expand=True,
                    on_click=lambda e: on_generate_click(e, log_view, stats_container),
                ),
                ft.ElevatedButton(
                    "📁 打开输出目录",
                    expand=True,
                    on_click=lambda e: on_open_output(e, log_view),
                ),
            ]),
        ], spacing=15),
        padding=20,
        height=220,  # 固定高度
    )
    
    def on_generate_click(e, log_view, stats_container):
        """开始生成按钮点击"""
        pass
    
    def on_open_output(e, log_view):
        """打开输出目录"""
        pass
    
    # 组装页面
    col = ft.Column([
        control_panel,      # 固定高度220px
        log_view,           # 弹性填充
        stats_container,    # 固定高度自动
    ], expand=True, spacing=10)
    
    main_container = ft.Container(
        content=col,
        padding=ft.Padding(0,50,0,0)
    )

    return main_container

def create_settings_page(router):
    """设置页"""
    col = ft.Column([
        ft.Text("⚙️ 全局设置", size=30, weight=ft.FontWeight.BOLD),
        
        ft.Row([
            ft.Text("配置路径:", width=100),
            ft.TextField(value="config.json", width=400),
        ]),
    ], spacing=20)

    container = ft.Container(
        content=col, 
        padding=ft.Padding(0,50,0,0), 
        expand=True
    )

    return container
