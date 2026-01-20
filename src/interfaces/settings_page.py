
import flet as ft
from pathlib import Path
import json
from typing import Callable, Dict, Any, Optional
from src.interfaces.base_page import BasePage

class SettingsPage(BasePage):
    """设置页 - 可视化编辑config.json"""
    
    def __init__(self, router, page: ft.Page):
        super().__init__(router, page)
        self.config_data: Optional[Dict[str, Any]] = None  # 加载的配置数据
    
    def load_config(self) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            config_path = Path("config.json")
            if config_path.exists():
                return json.loads(config_path.read_text(encoding='utf-8'))
            else:
                return self.get_default_config()
        except Exception:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        }
    
    def build(self) -> ft.Control:
        """构建设置表单"""
        # 加载配置
        self.config_data = self.load_config()
        
        # 创建表单组件
        output_dir_field = self.add_component(
            "output_dir_field",
            ft.TextField(
                value=self.config_data.get("output_dir", "./output"),
                label="输出目录",
                expand=True,
            )
        )
        
        template_dir_field = self.add_component(
            "template_dir_field",
            ft.TextField(
                value=self.config_data.get("template_dir", "./templates"),
                label="模板目录",
                expand=True,
            )
        )
        
        default_ns_field = self.add_component(
            "default_ns_field",
            ft.TextField(
                value=self.config_data.get("default_namespace", "minecraft:"),
                label="默认命名空间",
                expand=True,
            )
        )
        
        template_files_list = self.add_component(
            "template_files_list",
            ft.ListView(
                spacing=5,
                padding=10,
                auto_scroll=True,
                height=150,  # 固定高度
            )
        )
        
        # 加载模板文件列表
        self._load_template_files(template_files_list)
        
        add_template_btn = self.add_component(
            "add_template_btn",
            ft.ElevatedButton("添加模板文件", icon=ft.icons.ADD)
        )
        
        remove_template_btn = self.add_component(
            "remove_template_btn",
            ft.ElevatedButton("移除选中", icon=ft.icons.REMOVE)
        )
        
        # 规则列表（简化版，只显示type）
        rules_list = self.add_component(
            "rules_list",
            ft.ListView(
                spacing=5,
                padding=10,
                height=200,  # 固定高度
            )
        )
        
        self._load_rules_list(rules_list)
        
        save_btn = self.add_component(
            "save_btn",
            ft.ElevatedButton(
                "💾 保存配置",
                expand=True,
                bgcolor=ft.colors.GREEN,
                color="white",
            )
        )
        
        # 布局组装
        form = ft.Column([
            ft.Text("⚙️ 配置文件设置", size=24, weight=ft.FontWeight.BOLD),
            
            ft.Text("基础设置", size=18, weight=ft.FontWeight.BOLD),
            output_dir_field,
            template_dir_field,
            default_ns_field,
            
            ft.Divider(),
            
            ft.Text("模板文件", size=18, weight=ft.FontWeight.BOLD),
            template_files_list,
            ft.Row([add_template_btn, remove_template_btn], spacing=10),
            
            ft.Divider(),
            
            ft.Text("替换规则", size=18, weight=ft.FontWeight.BOLD),
            rules_list,
            
            ft.Divider(),
            
            save_btn,
        ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=form,
            padding=ft.padding.all(20),
            expand=True,
        )
    
    def _load_template_files(self, list_view: ft.ListView):
        """加载模板文件到列表"""
        template_dir = Path(self.config_data.get("template_dir", "./templates"))
        if template_dir.exists():
            template_files = self.config_data.get("template_files", [])
            
            for file in template_files:
                list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(file),
                        leading=ft.Icon(ft.icons.DESCRIPTION),
                    )
                )
    
    def _load_rules_list(self, list_view: ft.ListView):
        """加载替换规则到列表"""
        rules = self.config_data.get("replacements", [])
        
        if not rules:
            list_view.controls.append(
                ft.Text("暂无替换规则", color=ft.colors.GREY, size=14)
            )
            return
        
        for i, rule in enumerate(rules):
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(f"规则 {i+1}: {rule.get('type', 'unknown')}"),
                    subtitle=ft.Text(f"{len(rule.get('values', []))} 个值"),
                    leading=ft.Icon(ft.icons.LIST_ALT),
                )
            )
    
    # ========== 事件注册方法 ==========
    
    def register_save_event(self, handler: Callable):
        """注册保存按钮点击事件"""
        self.register_event("save_btn", "click", handler)
    
    def register_output_dir_change(self, handler: Callable):
        self.register_event("output_dir_field", "change", handler)
    
    def register_template_dir_change(self, handler: Callable):
        self.register_event("template_dir_field", "change", handler)
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前表单中的配置数据"""
        if not self.config_data:
            return {}
        
        # 从表单字段更新配置
        output_dir_field = self.get_component("output_dir_field")
        template_dir_field = self.get_component("template_dir_field")
        default_ns_field = self.get_component("default_ns_field")
        
        if output_dir_field:
            self.config_data["output_dir"] = output_dir_field.value
        
        if template_dir_field:
            self.config_data["template_dir"] = template_dir_field.value
        
        if default_ns_field:
            self.config_data["default_namespace"] = default_ns_field.value
        
        return self.config_data
