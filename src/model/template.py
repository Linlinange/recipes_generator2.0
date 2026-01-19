
import re
from pathlib import Path
from typing import List

class Template:
    """模板数据模型：只负责封装模板内容和占位符"""
    
    def __init__(self, path: Path):
        self.path = path
        self.content = path.read_text(encoding="utf-8")
        self.placeholders = self._extract_placeholders()
    
    def _extract_placeholders(self) -> List[str]:
        """提取并去重占位符（保持原始顺序）"""
        pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
        matches = pattern.findall(self.content)
        
        # 去重但保持顺序
        seen = set()
        result = []
        for m in matches:
            if m not in seen and m not in {"modid", "modid_safe"}:
                seen.add(m)
                result.append(m)
        return result