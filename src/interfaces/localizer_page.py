import flet as ft
from src.interfaces.base_page import BasePage


class LocalizerPage(BasePage):
    """
    LocalizerPage - 本地化页（占位UI）
    职责：纯UI展示，无业务逻辑
    """
    
    def __init__(self, router, page: ft.Page):
        super().__init__(router, page)
        # 不依赖任何Service
    
    def build(self) -> ft.Control:
        """纯UI，不绑定业务事件"""
        return ft.Container(
            content=ft.Column([
                ft.Text("📄 本地化工具", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("🚧 功能开发中...", size=16, color=ft.colors.ORANGE),
                ft.Text("敬请期待", size=14, color=ft.colors.GREY_400),
            ], expand=True, spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.all(40),
            alignment=ft.alignment.center
        )