"""
SettingsService - 配置业务服务
职责：持有配置数据，调用DAO进行读写，提供模板扫描
"""

import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.model.config import Config
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader


class SettingsService:
    """配置业务服务"""
    
    def __init__(self):
        
        # 核心数据：配置对象
        self.config: Optional[Config] = None
        
        # 扫描状态
        self.is_scanning = False
        self.last_scan_result: List[Path] = []
        self.last_scan_error: Optional[str] = None
    
    # ==================== 核心方法（供SettingsPage调用） ====================
    
    def load_config(self, config_path: str = "config.json") -> bool:
        """
        加载配置文件（调用ConfigDAO）
        参数:
            config_path: 配置文件路径，默认 "config.json"
        返回:
            成功返回True，失败返回False
        """
        try:
            self.config = ConfigDAO.load(config_path)
            self.last_scan_error = None  # 清除错误状态
            return True
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在: {config_path}")
            self.config = self._get_default_config()
            return False
        except json.JSONDecodeError:
            print(f"❌ 配置文件格式错误（不是有效JSON）")
            self.config = self._get_default_config()
            return False
        except Exception as ex:
            print(f"❌ 加载配置失败: {ex}")
            self.config = self._get_default_config()
            return False
    
    def save_config(self, config_path: str = "config.json") -> bool:
        """
        保存配置到文件（调用ConfigDAO）
        参数:
            config_path: 保存路径，默认 "config.json"
        返回:
            成功返回True，失败返回False
        """
        if not self.config:
            print("❌ 没有可保存的配置")
            return False
        
        try:
            success = ConfigDAO.save(self.config, config_path)
            if success:
                print(f"✅ 配置已保存到: {config_path}")
            return success
        except Exception as ex:
            print(f"❌ 保存配置失败: {ex}")
            return False
    
    def scan_templates(self, template_dir: Optional[str] = None) -> List[Path]:
        """
        扫描模板目录（调用TemplateLoader）
        参数:
            template_dir: 目录路径，None则使用config中的路径
        返回:
            模板文件Path列表（已排序）
        """
        # 确定扫描目录
        if template_dir:
            scan_path = Path(template_dir)
        elif self.config:
            scan_path = Path(self.config.template_dir)
        else:
            scan_path = Path("./templates")
        
        self.is_scanning = True
        self.last_scan_error = None
        
        try:
            # 调用DAO扫描
            templates = TemplateLoader.scan_directory(scan_path)
            self.last_scan_result = templates
            print(f"✅ 扫描成功，找到 {len(templates)} 个模板")
            return templates
        except Exception as ex:
            print(f"❌ 扫描模板目录失败: {ex}")
            self.last_scan_error = str(ex)
            self.last_scan_result = []
            return []
        finally:
            self.is_scanning = False
    
    def add_template(self, filename: str) -> bool:
        """
        添加模板到配置
        参数:
            filename: 模板文件名（不含路径）
        返回:
            成功返回True（已去重）
        """
        if not self.config:
            print("❌ 配置未加载")
            return False
        
        if filename not in self.config.template_files:
            self.config.template_files.append(filename)
            print(f"➕ 已添加模板: {filename}")
            return True
        
        print(f"⚠️ 模板已存在: {filename}")
        return False
    
    def remove_template(self, filename: str) -> bool:
        """
        从配置中移除模板
        参数:
            filename: 模板文件名
        返回:
            成功返回True
        """
        if not self.config:
            print("❌ 配置未加载")
            return False
        
        if filename in self.config.template_files:
            self.config.template_files.remove(filename)
            print(f"➖ 已移除模板: {filename}")
            return True
        
        print(f"⚠️ 模板不存在: {filename}")
        return False
    
    def update_config_from_form(self, output_dir: str, template_dir: str, namespace: str):
        """
        从表单更新配置对象
        参数:
            output_dir: 输出目录
            template_dir: 模板目录
            namespace: 默认命名空间
        """
        if not self.config:
            print("❌ 配置未加载")
            return
        
        self.config.output_dir = output_dir
        self.config.template_dir = template_dir
        self.config.default_namespace = namespace
        print(f"📄 配置已更新: {output_dir}, {template_dir}, {namespace}")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        获取配置字典（供其他Service/页面使用）
        返回:
            完整的配置字典
        """
        if not self.config:
            return self._get_default_config().to_dict()
        return self.config.to_dict()
    
    def get_selected_templates(self) -> List[str]:
        """
        获取已选择的模板列表
        返回:
            模板文件名列表（副本）
        """
        if not self.config:
            return []
        return self.config.template_files.copy()
    
    def has_config(self) -> bool:
        """
        检查是否已加载配置
        返回:
            bool
        """
        return self.config is not None
    
    def validate_config(self) -> List[str]:
        """
        验证配置有效性
        返回:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        if not self.config:
            errors.append("配置未加载")
            return errors
        
        # 验证输出目录
        if not self.config.output_dir:
            errors.append("输出目录不能为空")
        else:
            try:
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
            except Exception as ex:
                errors.append(f"输出目录无效: {ex}")
        
        # 验证模板目录
        if not self.config.template_dir:
            errors.append("模板目录不能为空")
        elif not Path(self.config.template_dir).exists():
            errors.append(f"模板目录不存在: {self.config.template_dir}")
        
        # 验证命名空间
        if not self.config.default_namespace:
            errors.append("默认命名空间不能为空")
        elif ":" not in self.config.default_namespace:
            errors.append("命名空间必须包含 ':' 符号")
        
        # 验证模板文件
        if not self.config.template_files:
            errors.append("至少选择一个模板文件")
        
        # 验证替换规则
        for rule in self.config.rules:
            if not rule.values:
                errors.append(f"规则 {rule.type} 没有值")
        
        return errors
    
    # ==================== 内部辅助方法 ====================
    
    def _get_default_config(self) -> Config:
        """获取默认配置对象"""
        return Config({
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        })