# src/interfaces/localizer_page.py

import flet as ft
from src.interfaces.base_page import BasePage
from src.service.localizer_service import LocalizerService


class LocalizerPage(BasePage):
    """
    LocalizerPage - 本地化页
    职责：UI展示 + 调用LocalizerService
    """
    
    def __init__(self, router, page: ft.Page, localizer_service: LocalizerService):
        super().__init__(router, page)
        self.localizer_service = localizer_service  # 依赖注入
        
        # 自动加载配置并显示状态
        self._load_initial_config()
    
    def _load_initial_config(self):
        """页面加载时同步配置"""
        if self.localizer_service.reload_config():
            self.log_message("✅ 本地化配置已同步")
        else:
            self.log_message("⚠️ 本地化配置加载失败", is_warning=True)
    
    def build(self) -> ft.Control:
        """构建UI并绑定事件"""
        # 控制面板
        process_btn = ft.ElevatedButton(
            "🌐 处理翻译",
            icon=ft.icons.TRANSLATE,
            on_click=self._handle_process_translation,
            disabled=True  # 默认禁用，等配置加载成功后再启用
        )
        
        # 语言选择下拉框（预留）
        language_dropdown = ft.Dropdown(
            label="目标语言",
            options=[
                ft.dropdown.Option("en_us", "English"),
                ft.dropdown.Option("zh_cn", "简体中文"),
                ft.dropdown.Option("ja_jp", "日本語"),
            ],
            value="en_us",
            disabled=True
        )
        
        # 日志区域
        log_view = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)
        
        # 布局组装
        control_panel = ft.Container(
            content=ft.Column([
                ft.Text("📄 本地化工具", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([process_btn, language_dropdown], spacing=20),
                ft.Text("🚧 核心功能开发中...", size=12, color=ft.colors.ORANGE),
            ], spacing=15),
            padding=20,
            bgcolor="#DDDDEE",
            height=150,
        )
        
        return ft.Column([
            control_panel,
            log_view,
        ], expand=True, spacing=10)
    
    # ==================== 事件处理器 ====================
    
    def _handle_process_translation(self, e: ft.ControlEvent):
        """处理翻译按钮点击"""
        # 示例：处理第一个模板
        success = self.localizer_service.process_translation("example.json")
        
        if success:
            self.log_message("✅ 翻译处理完成")
        else:
            self.log_message("❌ 翻译处理失败", is_error=True)
    
    # ==================== 辅助方法 ====================
    
    def log_message(self, message: str, is_error: bool = False, is_warning: bool = False, is_info: bool = False):
        """日志消息"""
        log_view = self.get_component("log_view")
        color = "red" if is_error else ("orange" if is_warning else ("blue" if is_info else None))
        log_view.controls.append(ft.Text(message, size=12, color=color))
        log_view.update()