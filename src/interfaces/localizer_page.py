
import flet as ft
from pathlib import Path
import sys
from src.interfaces.base_page import BasePage

sys.path.append(str(Path(__file__).parent.parent.parent))

class LocalizerPage(BasePage):
    """生成器页面类 - 纯UI"""
    
    def build(self) -> ft.Control:
        """只创建UI组件，不绑定具体事件处理"""
        
        # 控制面板组件
        
        localize_btn = self.add_component(
            "localize_btn",
            ft.ElevatedButton("📝 开始本地化", expand=True, width=200)
        )
        
        open_btn = self.add_component(
            "open_btn",
            ft.ElevatedButton("📁 打开输出目录", expand=True, width=200)
        )
        
        # 日志区域
        log_view = self.add_component(
            "log_view",
            ft.ListView(
                expand=True,
                spacing=5,
                padding=10,
                auto_scroll=True,
            )
        )
        
        # 统计区域
        stats_container = self.add_component(
            "stats_container",
            ft.Container(
                content=ft.Text("总数: 0 个文件, 0 个条目", size=14, weight=ft.FontWeight.BOLD),
                padding=10,
                bgcolor="#DDDDEE",
                border_radius=5,
            )
        )
        
        # 布局组装
        control_panel = ft.Container(
            content=ft.Column([
                ft.Text("📄 本地化工具", size=24, weight=ft.FontWeight.BOLD),
                
                ft.Row([
                    localize_btn,
                    open_btn,
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="#DDDDEE",
            height=220,
        )
        
        return ft.Column([
            control_panel,
            log_view,
            stats_container,
        ], expand=True, spacing=10)
    
    # ========== 事件注册方法（由run_flet调用） ==========
    
    def register_localize_event(self, handler: callable):
        """注册开始本地化按钮点击事件"""
        self.register_event("localize_btn", "click", handler)
    
    def register_open_event(self, handler: callable):
        """注册打开目录按钮点击事件"""
        self.register_event("open_btn", "click", handler)
