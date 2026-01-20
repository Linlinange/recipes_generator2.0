
import flet as ft
from pathlib import Path
from typing import Optional, List, Dict, Any
from src.interfaces.base_page import BasePage
from src.model.config import Config

class SettingsPage(BasePage):
    """
    设置页 - 纯UI
    所有业务逻辑由 SettingsController 处理
    """
    
    def __init__(self, router, page: ft.Page):
        super().__init__(router, page)
        self.config: Optional[Config] = None
        
        # UI状态（仅用于展示）
        self._template_checkboxes: Dict[str, ft.Checkbox] = {}
        self._selected_count_text: ft.Text = ft.Text("已选择: 0 个模板", size=14)
        self._status_text: ft.Text = ft.Text("", size=12, color=ft.colors.ORANGE)
        self._refresh_btn: Optional[ft.ElevatedButton] = None
    
    def build(self) -> ft.Control:
        """构建页面UI"""
        self.config = self.get_default_config()
        
        # 配置文件选择区域（新增）
        config_file_field = self.add_component(
            "config_file_field",
            ft.TextField(
                label="配置文件路径",
                value="config.json",
                expand=4,
            )
        )
        
        load_config_btn = self.add_component(
            "load_config_btn",
            ft.ElevatedButton("📂 加载配置", expand=1, height=50)
        )
        
        # 基础设置区域
        output_dir_field = self.add_component(
            "output_dir_field",
            ft.TextField(label="输出目录", expand=True, disabled=True)
        )
        
        template_dir_field = self.add_component(
            "template_dir_field",
            ft.TextField(label="模板目录", expand=True, disabled=True)
        )
        
        default_ns_field = self.add_component(
            "default_ns_field",
            ft.TextField(label="默认命名空间", expand=True, disabled=True)
        )
        
        # 模板管理区域
        self._status_text.value = "等待加载配置..."
        
        template_list_view = self.add_component(
            "template_list_view",
            ft.ListView(
                spacing=5,
                padding=10,
                auto_scroll=True,
                height=300,
            )
        )
        
        # 操作按钮行
        self._refresh_btn = self.add_component(
            "refresh_btn", 
            ft.ElevatedButton(
                "🔄 刷新模板列表",
                icon=ft.icons.REFRESH,
                disabled=True
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
        
        # 保存按钮
        save_btn = self.add_component(
            "save_btn",
            ft.ElevatedButton(
                "💾 保存配置",
                expand=True,
                bgcolor=ft.colors.BLUE,
                color="white",
                disabled=True
            )
        )
        
        # 布局组装
        return ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 配置文件设置", size=24, weight=ft.FontWeight.BOLD),
                
                # 配置文件选择（新增）
                ft.Row([
                    config_file_field,
                    load_config_btn,
                ], spacing=10),
                
                ft.Divider(),
                
                # 基础设置
                ft.Text("基础设置", size=18, weight=ft.FontWeight.BOLD),
                output_dir_field,
                template_dir_field,
                default_ns_field,
                
                ft.Divider(),
                
                # 模板文件管理
                ft.Text("模板文件管理", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self._refresh_btn,
                    self.get_component("selected_count_text")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self._status_text,
                template_list_view,
                
                ft.Divider(),
                
                # 替换规则列表
                ft.Text("替换规则", size=18, weight=ft.FontWeight.BOLD),
                rules_list_view,
                
                ft.Divider(),
                
                # 保存按钮
                save_btn,
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20),
        )
    
    # ==================== Controller 调用的接口 ====================
    
    def load_config_ui(self, config: Config):
        """
        加载配置并更新UI（Controller调用）
        参数:
            config: 已加载的Config对象
        """
        self.config = config
        
        # 更新基础字段
        self.get_component("output_dir_field").value = config.output_dir
        self.get_component("output_dir_field").disabled = False
        
        self.get_component("template_dir_field").value = config.template_dir
        self.get_component("template_dir_field").disabled = False
        
        self.get_component("default_ns_field").value = config.default_namespace
        self.get_component("default_ns_field").disabled = False
        
        # 启用按钮
        self._refresh_btn.disabled = False
        self.get_component("save_btn").disabled = False
        
        self.page.update()
    
    def update_template_list(self, available_templates: List[Path], status_message: str = ""):
        """
        更新模板列表（Controller调用）
        参数:
            available_templates: 目录中扫描到的所有模板文件路径
            status_message: 状态提示信息
        """
        list_view = self.get_component("template_list_view")
        list_view.controls.clear()
        self._template_checkboxes.clear()
        
        if not self.config:
            return
        
        # 构建复选框列表
        for template_path in sorted(available_templates):
            filename = template_path.name
            
            # 判断该模板是否已在配置中（初始选中状态）
            is_checked = filename in self.config.template_files
            
            # 创建复选框
            checkbox = ft.Checkbox(
                value=is_checked,
                label=filename,
                tristate=False,
                on_change=lambda e, f=filename: self._on_template_checkbox_change(f, e.control.value)
            )
            self._template_checkboxes[filename] = checkbox
            
            # 创建ListTile（整行可点击）
            list_tile = ft.ListTile(
                leading=checkbox,
                title=ft.Text(filename, size=14),
                selected=is_checked,
                on_click=lambda e, f=filename: self._on_template_tile_click(f),
            )
            list_view.controls.append(list_tile)
        
        # 更新状态文本
        self._status_text.value = status_message
        self._status_text.color = ft.colors.GREEN if "成功" in status_message else ft.colors.ORANGE
        
        # 更新选中计数
        self._update_selected_count()
        
        self.page.update()
    
    def update_rules_list(self):
        """
        更新替换规则列表（Controller调用）
        """
        if not self.config:
            return
        
        rules_list = self.get_component("rules_list_view")
        rules_list.controls.clear()
        
        if not self.config.rules:
            rules_list.controls.append(ft.Text("暂无替换规则", color=ft.colors.GREY, size=14))
            return
        
        for i, rule in enumerate(self.config.rules):
            rules_list.controls.append(ft.ListTile(
                title=ft.Text(f"规则 {i+1}: {rule.type}"),
                subtitle=ft.Text(f"{len(rule.values)} 个值 • {rule.description or '无描述'}"),
                leading=ft.Icon(ft.icons.LIST_ALT),
                trailing=ft.IconButton(
                    ft.icons.EDIT,
                    tooltip="编辑规则（开发中）",
                    on_click=lambda e, idx=i: self._show_placeholder("编辑规则功能开发中")
                ),
            ))
        
        self.page.update()
    
    def show_status_message(self, message: str, is_error: bool = False):
        """
        显示状态消息（Controller调用）
        参数:
            message: 消息内容
            is_error: True=红色错误，False=橙色提示
        """
        self._status_text.value = message
        self._status_text.color = ft.colors.RED if is_error else ft.colors.ORANGE
        self._status_text.update()
    
    def show_save_success(self):
        """显示保存成功动画（Controller调用）"""
        save_btn = self.get_component("save_btn")
        if not save_btn:
            return
        
        # 保存原始样式
        original_style = {
            "text": save_btn.text,
            "bgcolor": save_btn.bgcolor,
            "color": save_btn.color
        }
        
        # 更新为成功样式
        save_btn.text = "✅ 保存成功"
        save_btn.bgcolor = ft.colors.GREEN
        save_btn.update()
        
        # 3秒后恢复
        def restore():
            save_btn.text = original_style["text"]
            save_btn.bgcolor = original_style["bgcolor"]
            save_btn.update()
        
        self.page.run_task(restore, delay=3)
    
    def set_refresh_button_loading(self, loading: bool):
        """
        设置刷新按钮的加载状态（Controller调用）
        参数:
            loading: True=显示加载中，False=恢复
        """
        if loading:
            self._refresh_btn.text = "⏳ 扫描中..."
            self._refresh_btn.disabled = True
        else:
            self._refresh_btn.text = "🔄 刷新模板列表"
            self._refresh_btn.disabled = False
        self._refresh_btn.update()
    
    # ==================== 内部UI交互 ====================
    
    def _on_template_tile_click(self, filename: str):
        """
        模板项点击事件 - 转发给Controller处理
        """
        controller = getattr(self.page, '_settings_controller', None)
        if controller:
            controller.handle_template_toggle(filename)
    
    def _on_template_checkbox_change(self, filename: str, is_checked: bool):
        """
        复选框状态变更事件 - 转发给Controller处理
        """
        controller = getattr(self.page, '_settings_controller', None)
        if controller:
            controller.handle_template_checkbox_change(filename, is_checked)
    
    def _update_selected_count(self):
        """更新选中数量显示"""
        if not self.config:
            count = 0
        else:
            count = len(self.config.template_files)
        
        self._selected_count_text.value = f"已选择: {count} 个模板"
        
        # 根据数量变色警示
        if count == 0:
            self._selected_count_text.color = ft.colors.RED
        elif count > 20:
            self._selected_count_text.color = ft.colors.BLUE
        else:
            self._selected_count_text.color = ft.colors.GREY_600
        
        self._selected_count_text.update()
    
    def _show_placeholder(self, message: str):
        """占位提示"""
        print(f"🚧 {message}")
    
    # ==================== 核心数据接口 ====================
    
    def get_default_config(self) -> Config:
        """返回默认配置（首次加载用）"""
        return Config({
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        })
    
    def get_config_from_ui(self) -> dict:
        """
        从UI收集配置数据（Controller保存时调用）
        返回: 完整的配置字典
        """
        if not self.config:
            raise ValueError("配置未加载")
        
        # 基础字段从UI读取（用户可能手动修改）
        output_dir = self.get_component("output_dir_field").value
        template_dir = self.get_component("template_dir_field").value
        namespace = self.get_component("default_ns_field").value
        
        return {
            "output_dir": output_dir,
            "template_dir": template_dir,
            "default_namespace": namespace,
            "template_files": self.config.template_files.copy(),
            "replacements": [
                {
                    "type": rule.type,
                    "values": rule.values,
                    "extra": rule.extra,
                    "enabled": rule.enabled,
                    "description": rule.description,
                }
                for rule in self.config.rules
            ]
        }
