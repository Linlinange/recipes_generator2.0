"""
设置页控制器 - 所有业务逻辑中心
职责：配置加载、模板扫描、保存、状态管理等
"""

import json
from pathlib import Path
from typing import Optional, List
import threading
import time

import flet as ft
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader
from src.interfaces.settings_page import SettingsPage
from src.model.config import Config


class SettingsController:
    """
    SettingsPage的控制器，负责所有业务逻辑
    UI事件 → Controller → DAO/Service → UI更新
    """
    
    def __init__(self, page: SettingsPage):
        """
        初始化控制器
        参数:
            page: SettingsPage实例
        """
        self.page = page
        # 在Page上保存Controller引用，供Page转发事件
        setattr(page.page, '_settings_controller', self)
        
        # 内部状态
        self._current_config_path: str = "config.json"
        self._scan_delay_timer: Optional[threading.Timer] = None
        
        # 绑定所有UI事件
        self._bind_events()
        
        # 初始加载配置
        self._load_initial_config()
    
    # ==================== 事件绑定 ====================
    
    def _bind_events(self):
        """绑定所有UI事件到处理器"""
        # 配置文件加载
        load_btn = self.page.get_component("load_config_btn")
        if load_btn:
            load_btn.on_click = self._handle_load_config
        
        # 刷新模板列表
        refresh_btn = self.page.get_component("refresh_btn")
        if refresh_btn:
            refresh_btn.on_click = self._handle_refresh_templates
        
        # 保存配置
        save_btn = self.page.get_component("save_btn")
        if save_btn:
            save_btn.on_click = self._handle_save_config
        
        # 模板目录变更（带延迟扫描）
        template_dir_field = self.page.get_component("template_dir_field")
        if template_dir_field:
            template_dir_field.on_change = self._on_template_dir_change
        
        # 输出目录变更（可选：实时验证）
        output_dir_field = self.page.get_component("output_dir_field")
        if output_dir_field:
            output_dir_field.on_change = self._on_output_dir_change
    
    # ==================== 初始加载 ====================
    
    def _load_initial_config(self):
        """页面加载时自动加载默认配置"""
        self._load_config_from_path(self._current_config_path)
    
    # ==================== 事件处理器 ====================
    
    def _handle_load_config(self, e: ft.ControlEvent):
        """
        处理"加载配置"按钮点击
        从配置文件字段读取路径并加载
        """
        config_file_field = self.page.get_component("config_file_field")
        config_path = config_file_field.value.strip() if config_file_field else "config.json"
        
        if not config_path:
            self.page.show_status_message("❌ 配置文件路径不能为空", is_error=True)
            return
        
        self._current_config_path = config_path
        self._load_config_from_path(config_path)
    
    def _handle_refresh_templates(self, e: ft.ControlEvent):
        """
        处理"刷新模板列表"按钮点击
        重新扫描模板目录并更新UI
        """
        if not self.page.config:
            self.page.show_status_message("❌ 请先加载配置", is_error=True)
            return
        
        # 异步扫描避免阻塞UI
        self._scan_templates_async()
    
    def _handle_save_config(self, e: ft.ControlEvent):
        """
        处理"保存配置"按钮点击
        从UI收集数据并保存到文件
        """
        try:
            # 验证配置完整性
            validation_errors = self._validate_config()
            if validation_errors:
                self.page.show_status_message(f"❌ 验证失败: {validation_errors[0]}", is_error=True)
                return
            
            # 收集UI数据
            config_dict = self.page.get_config_from_ui()
            
            # 创建Config对象并保存
            config = Config.from_dict(config_dict)
            success = ConfigDAO.save(config, self._current_config_path)
            
            if success:
                self.page.show_save_success()
                self.page.show_status_message(f"✅ 配置已保存到: {self._current_config_path}", is_error=False)
            else:
                self.page.show_status_message("❌ 保存失败，请检查文件权限", is_error=True)
                
        except Exception as ex:
            self.page.show_status_message(f"❌ 保存异常: {ex}", is_error=True)
            print(f"Save error: {ex}")  # 调试日志
    
    def _on_template_dir_change(self, e: ft.ControlEvent):
        """
        模板目录字段变更事件
        延迟1秒后自动刷新（避免用户输入过程中频繁扫描）
        """
        # 取消之前的定时器
        if self._scan_delay_timer:
            self._scan_delay_timer.cancel()
        
        # 设置新的延迟扫描（1秒后）
        self._scan_delay_timer = threading.Timer(1.0, self._scan_templates_async)
        self._scan_delay_timer.start()
        
        # 实时更新状态（可选）
        new_dir = e.control.value if e.control else ""
        self.page.show_status_message(f"⏳ 目录已更改，1秒后将自动扫描: {new_dir}")
    
    def _on_output_dir_change(self, e: ft.ControlEvent):
        """
        输出目录字段变更事件
        验证目录可写性
        """
        output_dir = e.control.value if e.control else ""
        if not output_dir:
            return
        
        dir_path = Path(output_dir)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            # 测试写入权限
            test_file = dir_path / ".write_test"
            test_file.touch(exist_ok=True)
            test_file.unlink()
            self.page.show_status_message(f"✅ 输出目录有效: {output_dir}", is_error=False)
        except Exception as ex:
            self.page.show_status_message(f"⚠️ 输出目录可能无效: {ex}", is_error=True)
    
    # ==================== 核心逻辑方法 ====================
    
    def _load_config_from_path(self, config_path: str):
        """
        从指定路径加载配置
        参数:
            config_path: 配置文件路径
        """
        try:
            self.page.show_status_message(f"⏳ 正在加载配置: {config_path}")
            self.page.set_refresh_button_loading(True)
            
            # 加载配置
            config = ConfigDAO.load(config_path)
            
            # 更新UI
            self.page.load_config_ui(config)
            
            # 扫描并更新模板列表
            self._scan_and_update_templates(config.template_dir)
            
            # 更新规则列表
            self.page.update_rules_list()
            
            self.page.show_status_message(f"✅ 配置加载成功", is_error=False)
            
        except FileNotFoundError:
            self.page.show_status_message(f"⚠️ 配置文件不存在: {config_path}", is_error=True)
            # 加载默认配置
            self.page.load_config_ui(self.page.get_default_config())
        except json.JSONDecodeError:
            self.page.show_status_message(f"❌ 配置文件格式错误（不是有效JSON）", is_error=True)
        except Exception as ex:
            self.page.show_status_message(f"❌ 加载失败: {ex}", is_error=True)
            print(f"Load config error: {ex}")
        finally:
            self.page.set_refresh_button_loading(False)
    
    def _scan_and_update_templates(self, template_dir: str):
        """
        扫描模板目录并更新UI
        参数:
            template_dir: 模板目录路径
        """
        try:
            dir_path = Path(template_dir)
            if not dir_path.exists():
                self.page.show_status_message(f"⚠️ 模板目录不存在: {template_dir}", is_error=True)
                self.page.update_template_list([], "目录不存在")
                return
            
            # 扫描模板
            templates = TemplateLoader.scan_directory(dir_path)
            
            # 更新UI
            self.page.update_template_list(templates, f"✅ 扫描成功，找到 {len(templates)} 个模板")
            
        except Exception as ex:
            self.page.show_status_message(f"❌ 扫描失败: {ex}", is_error=True)
            self.page.update_template_list([], "扫描失败")
    
    def _scan_templates_async(self):
        """
        异步扫描模板目录（不阻塞UI）
        """
        if not self.page.config:
            return
        
        # 显示加载状态
        self.page.set_refresh_button_loading(True)
        self.page.show_status_message("⏳ 正在扫描模板目录...")
        
        # 在后台线程执行扫描
        def scan_in_background():
            try:
                template_dir = self.page.config.template_dir
                dir_path = Path(template_dir)
                
                if not dir_path.exists():
                    self.page.show_status_message(f"⚠️ 模板目录不存在: {template_dir}", is_error=True)
                    return
                
                templates = TemplateLoader.scan_directory(dir_path)
                
                # 在主线程更新UI（Flet要求UI操作必须在主线程）
                def update_ui():
                    self.page.update_template_list(templates, f"✅ 扫描成功，找到 {len(templates)} 个模板")
                    self.page.set_refresh_button_loading(False)
                
                self.page.page.run_task(update_ui)
                
            except Exception as ex:
                def show_error():
                    self.page.show_status_message(f"❌ 扫描失败: {ex}", is_error=True)
                    self.page.set_refresh_button_loading(False)
                
                self.page.page.run_task(show_error)
        
        thread = threading.Thread(target=scan_in_background, daemon=True)
        thread.start()
    
    def _validate_config(self) -> List[str]:
        """
        验证配置有效性
        返回: 错误信息列表，空列表表示验证通过
        """
        errors = []
        
        try:
            # 验证输出目录
            output_dir = self.page.get_component("output_dir_field").value
            if not output_dir:
                errors.append("输出目录不能为空")
            else:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # 验证模板目录
            template_dir = self.page.get_component("template_dir_field").value
            if not template_dir:
                errors.append("模板目录不能为空")
            elif not Path(template_dir).exists():
                errors.append(f"模板目录不存在: {template_dir}")
            
            # 验证命名空间
            namespace = self.page.get_component("default_ns_field").value
            if not namespace:
                errors.append("默认命名空间不能为空")
            elif ":" not in namespace:
                errors.append("命名空间必须包含 ':' 符号（例如: minecraft:）")
            
            # 验证模板文件
            if not self.page.config.template_files:
                errors.append("至少选择一个模板文件")
            
        except Exception as ex:
            errors.append(f"验证异常: {ex}")
        
        return errors
    
    # ==================== 公共方法（供Page调用） ====================
    
    def handle_template_toggle(self, filename: str):
        """
        处理模板选择状态切换（Page转发调用）
        参数:
            filename: 模板文件名
        """
        checkbox = self.page._template_checkboxes.get(filename)
        if not checkbox:
            return
        
        # 如果复选框被禁用（正在加载），忽略操作
        if checkbox.disabled:
            return
        
        is_checked = checkbox.value
        
        # 更新配置
        if is_checked:
            if filename not in self.page.config.template_files:
                self.page.config.template_files.append(filename)
                self.page.show_status_message(f"➕ 已添加: {filename}", is_error=False)
        else:
            if filename in self.page.config.template_files:
                self.page.config.template_files.remove(filename)
                self.page.show_status_message(f"➖ 已移除: {filename}", is_error=False)
        
        # 更新计数
        self.page._update_selected_count()
    
    def handle_template_checkbox_change(self, filename: str, is_checked: bool):
        """
        复选框显式变更事件（Page转发调用）
        参数:
            filename: 模板文件名
            is_checked: 新的选中状态
        """
        # 复用toggle逻辑
        self.handle_template_toggle(filename)