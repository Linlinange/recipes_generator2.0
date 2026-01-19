
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ReplacementRule:
    """替换规则模型"""
    type: str
    values: List[str]
    extra: Dict[str, Dict[str, str]] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}

class Config:
    """配置数据容器"""
    
    def __init__(self, raw_data: Dict[str, Any]):
        self.output_dir = raw_data.get("output_dir", "./output")
        self.template_dir = raw_data.get("template_dir", "./templates")
        self.default_namespace = raw_data.get("default_namespace", "minecraft:")
        self.template_files = raw_data.get("template_files", [])
        
        # 解析替换规则
        self.rules = [
            ReplacementRule(**rule) 
            for rule in raw_data.get("replacements", [])
        ]