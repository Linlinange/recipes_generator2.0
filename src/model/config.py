
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, fields

@dataclass
class ReplacementRule:
    """替换规则模型 - 支持description，忽略未知字段"""
    type: str
    values: List[str]
    extra: Optional[Dict[str, Dict[str, str]]] = None
    enabled: bool = True
    description: str = ""  # ✅ 正式字段
    
    def __post_init__(self):
        # 确保extra有默认值
        if self.extra is None:
            self.extra = {}
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> 'ReplacementRule':
        """
        工厂方法：只提取已定义的字段，忽略未知参数
        """
        # 获取所有dataclass字段名
        field_names = {f.name for f in fields(cls)}
        
        # 过滤出已定义的字段
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        
        return cls(**filtered_data)

class Config:
    """配置数据容器"""
    
    def __init__(self, raw_data: Dict[str, Any]):
        self.output_dir = raw_data.get("output_dir", "./output")
        self.template_dir = raw_data.get("template_dir", "./templates")
        self.default_namespace = raw_data.get("default_namespace", "minecraft:")
        self.template_files = raw_data.get("template_files", [])
        
        # ✅ 使用工厂方法创建规则，自动忽略未知字段
        self.rules = [
            ReplacementRule.create(rule)
            for rule in raw_data.get("replacements", [])
        ]