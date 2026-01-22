from dataclasses import dataclass, field, fields
from typing import Dict, Any, Optional, List

@dataclass
class BatchItem:
    """
    批量生成项模型 - 支持材料/工具/食物/盔甲等各类模板参数
    作为LocalizationEngine的核心数据载体，封装ID、中文名、替换规则等元数据
    """
    id: str                       # 项ID (如 "minecraft:oak", "iron_sword")
    zh_cn: str                    # 中文名 (如 "橡木", "铁剑")
    namespace: str                # 命名空间 (如 "minecraft:", "")
    category: str = "material"    # 类别: material, tool, food, armor, block...
    skip_patterns: List[str] = field(default_factory=list)  # 跳过含这些词的模板
    replacements: Dict[str, str] = field(default_factory=dict)  # 专属替换规则
    description: str = ""         # 项描述
    
    def __post_init__(self):
        """确保容器字段有默认值"""
        if self.skip_patterns is None:
            self.skip_patterns = []
        if self.replacements is None:
            self.replacements = {}
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> 'BatchItem':
        """
        工厂方法：只提取已定义字段，忽略未知参数
        与ReplacementRule.create()保持一致的健壮性
        """
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，用于JSON输出"""
        return {
            "id": self.id,
            "zh_cn": self.zh_cn,
            "namespace": self.namespace,
            "category": self.category,
            "skip_patterns": self.skip_patterns,
            "replacements": self.replacements,
            "description": self.description
        }
    
    # ========== 业务方法（引擎直接调用） ==========
    
    def get_key_prefix(self) -> str:
        """
        生成键名前缀（提取ID的最后部分）
        如 "minecraft:oak" → "oak", "stripped_oak" → "stripped_oak"
        """
        return self.id.split(":")[-1]
    
    def should_skip_template(self, template_key: str) -> bool:
        """
        判断当前项是否应该跳过某个模板
        基于skip_patterns列表进行子字符串匹配
        skip_patterns列表不存在时(或为None)返回False
        
        示例:
            skip_patterns=["stripped", "log"] 会跳过 "stripped_oak_chair" 和 "oak_log_table"
        """
        if not self.skip_patterns:
            return False
        return any(pattern in template_key for pattern in self.skip_patterns)
    
    def apply_replacements(self, text: str) -> str:
        """
        应用项专属替换规则（后处理）
        只替换非元数据键（不以_开头）
        
        示例:
            {"木": "", "原木": "菌柄"} 会将 "基本橡木椅子" → "基本橡椅子"
        """
        result = text
        for old, new in self.replacements.items():
            # 跳过元数据键（如_material_zh_cn, _log等）
            if not old.startswith("_"):
                result = result.replace(old, new)
        # 清理多余空格
        return ''.join(result.split())
    
    def get_modid_safe(self) -> str:
        """
        生成安全的命名空间字符串
        minecraft: → "" (空)
        pfm: → "pfm_"
        """
        if self.namespace == "minecraft:":
            return ""
        return self.namespace.replace(":", "_")