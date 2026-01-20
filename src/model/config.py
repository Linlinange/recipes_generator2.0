from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, fields


@dataclass
class ReplacementRule:
    """替换规则模型 - 支持description，忽略未知字段"""
    type: str
    values: List[str]
    extra: Optional[Dict[str, Dict[str, str]]] = None
    enabled: bool = True
    description: str = ""
    
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

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，用于JSON输出"""
        return {
            "type": self.type,
            "values": self.values,
            "extra": self.extra,
            "enabled": self.enabled,
            "description": self.description
        }


class Config:
    """配置数据容器"""
    
    def __init__(self, raw_data: Dict[str, Any]):
        self.output_dir = raw_data.get("output_dir", "./output")
        self.template_dir = raw_data.get("template_dir", "./templates")
        self.default_namespace = raw_data.get("default_namespace", "minecraft:")
        self._template_files = raw_data.get("template_files", [])
        self._rules = [
            ReplacementRule.create(rule)
            for rule in raw_data.get("replacements", [])
        ]

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> 'Config':
        """从字典创建Config对象（兼容旧格式迁移）"""
        return cls(raw_data)

    @property
    def template_dir_path(self) -> Path:
        """返回: Path对象（已验证存在性）"""
        dir_path = Path(self.template_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"模板目录路径不是有效目录: {self.template_dir}")
        return dir_path

    @property
    def output_dir_path(self) -> Path:
        """返回: Path对象（已验证存在性）"""
        dir_path = Path(self.output_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"输出目录路径不是有效目录: {self.output_dir}")
        return dir_path

    @property
    def template_files(self) -> List[str]:
        """获取模板文件列表（只读）"""
        return self._template_files.copy()

    @template_files.setter
    def template_files(self, value: List[str]):
        """
        设置模板文件列表（自动去重、过滤空值）
        参数: value - 字符串列表或可以转换为字符串的可迭代对象
        """
        # 类型验证
        if not isinstance(value, (list, tuple)):
            raise TypeError("template_files必须是列表或元组类型")
        
        # 去重并过滤空字符串
        unique_files = []
        seen = set()
        for item in value:
            file_str = str(item).strip()
            if file_str and file_str not in seen:
                seen.add(file_str)
                unique_files.append(file_str)
        
        self._template_files = unique_files

    @property
    def rules(self) -> List[ReplacementRule]:
        """获取替换规则列表（只读）"""
        return self._rules.copy()

    @rules.setter
    def rules(self, value: List[Dict[str, Any]]):
        """
        设置替换规则列表（自动去重、创建Rule对象）
        参数: value - 字典列表或ReplacementRule对象列表
        """
        # 类型验证
        if not isinstance(value, (list, tuple)):
            raise TypeError("rules必须是字典列表或ReplacementRule对象列表")
        
        # 统一转换为字典
        rule_dicts = []
        for item in value:
            if isinstance(item, ReplacementRule):
                rule_dicts.append(item.to_dict())
            elif isinstance(item, dict):
                rule_dicts.append(item)
            else:
                raise TypeError("rules列表项必须是dict或ReplacementRule")
        
        # 去重逻辑（基于type+values组合去重）
        unique_rules = []
        seen_keys = set()
        for rule_dict in rule_dicts:
            # 创建ReplacementRule对象
            rule = ReplacementRule.create(rule_dict)
            
            # 生成唯一标识键（type + values排序后拼接）
            rule_key = (rule.type, tuple(sorted(rule.values)))
            if rule_key not in seen_keys:
                seen_keys.add(rule_key)
                unique_rules.append(rule)
        
        self._rules = unique_rules

    def to_dict(self) -> Dict[str, Any]:
        """返回: 完整的序列化字典，包含output_dir/template_files/rules等"""
        return {
            "output_dir": self.output_dir,
            "template_dir": self.template_dir,
            "default_namespace": self.default_namespace,
            "template_files": self.template_files,
            "replacements": [rule.to_dict() for rule in self.rules]
        }

    # ========== 新增：便捷的修改方法 ==========
    
    def add_template_file(self, filename: str) -> bool:
        """
        添加模板文件（如果已存在则跳过）
        返回: 是否成功添加（True=新增，False=已存在）
        """
        if not filename or not isinstance(filename, str):
            raise ValueError("filename必须是字符串")
        
        if filename in self._template_files:
            return False  # 已存在
        
        self._template_files.append(filename)
        return True
    
    def remove_template_file(self, filename: str) -> bool:
        """
        移除模板文件（如果不存在则跳过）
        返回: 是否成功移除（True=移除，False=不存在）
        """
        if filename in self._template_files:
            self._template_files.remove(filename)
            return True
        return False
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        添加替换规则（自动去重）
        返回: 是否成功添加（True=新增，False=已存在或无效）
        """
        try:
            new_rule = ReplacementRule.create(rule)
            rule_key = (new_rule.type, tuple(sorted(new_rule.values)))
            
            for existing_rule in self._rules:
                existing_key = (existing_rule.type, tuple(sorted(existing_rule.values)))
                if rule_key == existing_key:
                    return False  # 已存在
            
            self._rules.append(new_rule)
            return True
        except Exception:
            return False