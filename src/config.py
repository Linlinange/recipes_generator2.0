# src/config.py
import json
from pathlib import Path
from typing import Dict, List, Any

class ConfigManager:
    """
    配置管理器
    职责：加载 JSON 配置，兼容旧格式，提供类型安全访问
    对应原函数：load_config()
    """
    
    def __init__(self, path: str = "config.json"):
        self._data = self._load(path)
        self._migrate_old_format()  # 兼容 tree_types + tree_replacements
    
    def _load(self, path: str) -> Dict[str, Any]:
        """加载并解析 JSON 配置"""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件 {path} 不存在")
        
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def _migrate_old_format(self):
        """自动迁移旧格式（tree_types → replacements）"""
        if "tree_types" in self._data and "tree_replacements" in self._data:
            tree_replacement = {
                "type": "tree",
                "values": self._data["tree_types"],
                "extra": self._data["tree_replacements"],
                "enabled": True,
                "description": "树类型（旧格式自动迁移）"
            }
            self._data["replacements"] = [tree_replacement]
            del self._data["tree_types"], self._data["tree_replacements"]
    
    def get(self, key: str, default=None):
        """安全访问配置项"""
        return self._data.get(key, default)
    
    @property
    def output_dir(self) -> Path:
        """输出目录（Path 对象）"""
        return Path(self._data.get("output_dir", "./output"))
    
    @property
    def template_dir(self) -> Path:
        """模板目录（Path 对象）"""
        return Path(self._data.get("template_dir", "./templates"))
    
    @property
    def default_namespace(self) -> str:
        """默认命名空间"""
        return self._data.get("default_namespace", "minecraft:")
    
    def get_active_rules(self) -> List[Dict]:
        """获取启用的替换规则"""
        return [r for r in self._data.get("replacements", []) 
                if r.get("enabled", True)]
