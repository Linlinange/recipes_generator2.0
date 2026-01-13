# src/template.py
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple

class Template:
    """
    模板对象
    职责：封装单个模板文件的内容和占位符
    """
    
    # 静态常量：占位符正则和系统保留词
    PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")
    SYSTEM_KEYS = {"modid", "modid_safe"}
    
    def __init__(self, path: Path):
        self.path = path
        self._content = self._load()
        self.placeholders = self._scan()
    
    def _load(self) -> str:
        """读取模板文件内容"""
        return self.path.read_text(encoding="utf-8")
    
    def _scan(self) -> Set[str]:
        """扫描动态占位符（排除系统占位符）"""
        all_matches = self.PLACEHOLDER_PATTERN.findall(self._content)
        return set(all_matches) - self.SYSTEM_KEYS
    
    @property
    def content(self) -> str:
        """获取模板内容（只读）"""
        return self._content

class TemplateManager:
    """
    模板管理器
    职责：加载所有模板，返回 Template 对象
    对应原函数：load_templates()
    """
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def load_all(self, file_list: List[str]) -> Dict[str, Template]:
        """加载所有模板文件"""
        templates = {}
        for filename in file_list:
            path = self.template_dir / filename
            if not path.exists():
                print(f"⚠️  模板不存在: {path}，已跳过")
                continue
            templates[filename] = Template(path)
        return templates
