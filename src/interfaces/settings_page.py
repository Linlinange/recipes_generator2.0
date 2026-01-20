import flet as ft
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from src.interfaces.base_page import BasePage
from src.service.settings_service import SettingsService


class SettingsPage(BasePage):
    """
    SettingsPage - 设置页（内部绑定事件）
    职责：UI展示 + 直接调用SettingsService
    """
    
    def __init__(self, router, page: ft.Page, service: SettingsService):
        super().__init__(router, page)
        self.service = service  # 注入Service
        
        # UI状态
        self._template_checkboxes: Dict[str, ft.Checkbox] = {}
        self._selected_count_text: ft.Text = ft.Text("已选择: 0 个模板", size=14)
        self._status_text: ft.Text = ft.Text("等待加载配置...", size=12, color=ft.colors.ORANGE)
        self._refresh_btn: Optional[ft.ElevatedButton] = None
        self._save_btn: Optional[ft.ElevatedButton] = None
    
    def build(self) -> ft.Control:
        """构建UI并直接绑定事件"""
        # 初始加载配置
        if not self.service.has_config():
            self.service.load_config()
        
        # 配置文件选择区域
        config_file_field = self.add_component(
            "config_file_field",
            ft.TextField(
                label="配置文件路径",
                value="config.json",
                expand=True,
                disabled=False,
                on_change=self._on_config_path_change  # 内部绑定
            )
        )
        
        load_config_btn = self.add_component(
            "load_config_btn",
            ft.ElevatedButton(
                "📂 加载配置",
                icon=ft.icons.FOLDER_OPEN,
                on_click=self._handle_load_config  # 内部绑定
            )
        )
        
        # 基础设置区域
        output_dir_field = self.add_component(
            "output_dir_field",
            ft.TextField(
                label="输出目录",
                expand=True,
                disabled=False,
                on_change=self._on_output_dir_change  # 内部绑定
            )
        )
        
        template_dir_field = self.add_component(
            "template_dir_field",
            ft.TextField(
                label="模板目录",
                expand=True,
                disabled=False,
                on_change=self._on_template_dir_change  # 内部绑定
            )
        )
        
        default_ns_field = self.add_component(
            "default_ns_field",
            ft.TextField(
                label="默认命名空间",
                expand=True,
                disabled=False,
                on_change=self._on_namespace_change  # 内部绑定
            )
        )
        
        # 模板管理区域
        self._status_text.value = "等待加载配置..."
        
        template_list_view = self.add_component(
            "template_list_view",
            ft.ListView(spacing=5, padding=10, auto_scroll=True, height=300)
        )
        
        self._refresh_btn = self.add_component(
            "refresh_btn", 
            ft.ElevatedButton(
                "🔄 刷新模板列表",
                icon=ft.icons.REFRESH,
                disabled=False,
                on_click=self._handle_refresh_templates  # 内部绑定
            )
        )
        
        # 统计信息
        self._selected_count_text = self.add_component(
            "selected_count_text",
            self._selected_count_text
        )
        
        # 替换规则列表
        rules_list_view = self.add_component(
            "rules_list_view",
            ft.ListView(spacing=5, padding=10, height=200)
        )
        
        self._save_btn = self.add_component(
            "save_btn",
            ft.ElevatedButton(
                "💾 保存配置",
                expand=True,
                bgcolor=ft.colors.BLUE,
                color="white",
                disabled=False,
                on_click=self._handle_save_config  # 内部绑定
            )
        )
        
        # 布局组装
        return ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 配置文件设置", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([config_file_field, load_config_btn], spacing=10),
                ft.Divider(),
                ft.Text("基础设置", size=18, weight=ft.FontWeight.BOLD),
                output_dir_field,
                template_dir_field,
                default_ns_field,
                ft.Divider(),
                ft.Text("模板文件管理", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([self._refresh_btn, self.get_component("selected_count_text")], 
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self._status_text,
                template_list_view,
                ft.Divider(),
                ft.Text("替换规则", size=18, weight=ft.FontWeight.BOLD),
                rules_list_view,
                ft.Divider(),
                self._save_btn,
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20),
        )
    
    # ==================== 内部事件处理器 ====================
    
    def _handle_load_config(self, e: ft.ControlEvent):
        """加载配置按钮点击"""
        config_field = self.get_component("config_file_field")
        config_path = config_field.value if config_field else "config.json"
        
        success = self.service.load_config(config_path)
        if success:
            self._update_ui_from_service()
            self._scan_templates_async()
            self.show_status_message("✅ 配置加载成功", is_error=False)
        else:
            self.show_status_message("⚠️ 加载失败，使用默认配置", is_error=True)
    
    def _handle_refresh_templates(self, e: ft.ControlEvent):
        """刷新模板列表按钮点击"""
        self._scan_templates_async()
    
    def _handle_save_config(self, e: ft.ControlEvent):
        """保存配置按钮点击"""
        # 从UI收集数据到Service
        self._update_service_from_ui()
        
        # 验证
        errors = self.service.validate_config()
        if errors:
            self.show_status_message(f"❌ {errors[0]}", is_error=True)
            return
        
        # 保存
        config_field = self.get_component("config_file_field")
        save_path = config_field.value if config_field else "config.json"
        
        success = self.service.save_config(save_path)
        if success:
            self._show_save_success()
            self.show_status_message(f"✅ 配置已保存", is_error=False)
        else:
            self.show_status_message("❌ 保存失败", is_error=True)
    
    def _on_config_path_change(self, e: ft.ControlEvent):
        """配置文件路径变更"""
        # 可以添加路径验证
        pass
    
    def _on_output_dir_change(self, e: ft.ControlEvent):
        """输出目录变更"""
        # 可以实时验证目录有效性
        pass
    
    def _on_template_dir_change(self, e: ft.ControlEvent):
        """模板目录变更"""
        # 延迟1秒自动扫描
        def delayed_scan():
            import time
            time.sleep(1.0)
            self._scan_templates_async()
        threading.Thread(target=delayed_scan, daemon=True).start()
    
    def _on_namespace_change(self, e: ft.ControlEvent):
        """命名空间变更"""
        pass
    
    # ==================== UI更新方法 ====================
    
    def _update_ui_from_service(self):
        """从Service更新UI"""
        if not self.service.has_config():
            return
        
        config_dict = self.service.get_config_dict()
        
        self.get_component("output_dir_field").value = config_dict["output_dir"]
        self.get_component("template_dir_field").value = config_dict["template_dir"]
        self.get_component("default_ns_field").value = config_dict["default_namespace"]
        
        self._update_selected_count()
        self.page.update()
    
    def _update_service_from_ui(self):
        """从UI更新Service"""
        output_dir = self.get_component("output_dir_field").value
        template_dir = self.get_component("template_dir_field").value
        namespace = self.get_component("default_ns_field").value
        
        self.service.update_config_from_form(output_dir, template_dir, namespace)
    
    def _scan_templates_async(self):
        """异步扫描模板"""
        if not self.service.has_config():
            return
        
        self.set_refresh_button_loading(True)
        
        def scan_in_background():
            templates = self.service.scan_templates()
            
            def update_ui():
                self._update_template_list(templates, f"✅ 扫描成功，找到 {len(templates)} 个模板")
                self.set_refresh_button_loading(False)
            
            self.page.run_task(update_ui)
        
        threading.Thread(target=scan_in_background, daemon=True).start()
    
    def _update_template_list(self, templates: List[Path], status_message: str = ""):
        """更新模板列表UI"""
        list_view = self.get_component("template_list_view")
        list_view.controls.clear()
        self._template_checkboxes.clear()
        
        selected_templates = self.service.get_selected_templates()
        
        for template_path in sorted(templates):
            filename = template_path.name
            is_checked = filename in selected_templates
            
            checkbox = ft.Checkbox(
                value=is_checked,
                label=filename,
                on_change=lambda e, f=filename: self._on_template_checkbox_change(f, e.control.value)
            )
            self._template_checkboxes[filename] = checkbox
            
            list_tile = ft.ListTile(
                leading=checkbox,
                title=ft.Text(filename, size=14),
                selected=is_checked,
                on_click=lambda e, f=filename: self._on_template_tile_click(f),
            )
            list_view.controls.append(list_tile)
        
        self._status_text.value = status_message
        self._status_text.color = ft.colors.GREEN if "成功" in status_message else ft.colors.ORANGE
        self._update_selected_count()
        self.page.update()
    
    # ==================== 辅助方法 ====================
    
    def _on_template_tile_click(self, filename: str):
        """模板项点击：切换复选框"""
        checkbox = self._template_checkboxes.get(filename)
        if checkbox:
            checkbox.value = not checkbox.value
            self.page.update()
            self._on_template_checkbox_change(filename, checkbox.value)
    
    def _on_template_checkbox_change(self, filename: str, is_checked: bool):
        """复选框变更"""
        if is_checked:
            self.service.add_template(filename)
            self.show_status_message(f"➕ 已添加: {filename}", is_error=False)
        else:
            self.service.remove_template(filename)
            self.show_status_message(f"➖ 已移除: {filename}", is_error=False)
        
        self._update_selected_count()
    
    def _update_selected_count(self):
        """更新选中计数"""
        count = len(self.service.get_selected_templates())
        self._selected_count_text.value = f"已选择: {count} 个模板"
        self._selected_count_text.color = ft.colors.RED if count == 0 else ft.colors.GREY_600
        self._selected_count_text.update()
    
    def show_status_message(self, message: str, is_error: bool = False):
        """显示状态消息"""
        self._status_text.value = message
        self._status_text.color = ft.colors.RED if is_error else ft.colors.ORANGE
        self._status_text.update()
    
    def set_refresh_button_loading(self, loading: bool):
        """设置刷新按钮加载状态"""
        if loading:
            self._refresh_btn.text = "⏳ 扫描中..."
            self._refresh_btn.disabled = True
        else:
            self._refresh_btn.text = "🔄 刷新模板列表"
            self._refresh_btn.disabled = False
        self.page.update()
    
    def _show_save_success(self):
        """显示保存成功动画"""
        original = {
            "text": self._save_btn.text,
            "bgcolor": self._save_btn.bgcolor,
        }
        
        self._save_btn.text = "✅ 保存成功"
        self._save_btn.bgcolor = ft.colors.GREEN
        self.page.update()
        
        def restore():
            self._save_btn.text = original["text"]
            self._save_btn.bgcolor = original["bgcolor"]
            self.page.update()
        
        self.page.run_task(restore, delay=3)