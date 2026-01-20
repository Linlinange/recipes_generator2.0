
import re
from pathlib import Path
from typing import List

class Template:
    """模板数据模型：只负责封装模板内容和占位符"""
    
    def __init__(self, path: Path):
        self.path = path
        self.content = ""
        self.placeholders = []
        
        # 初始化时加载内容并提取占位符
        self._load_content()
        self.placeholders = self._extract_placeholders()
    
    def _load_content(self) -> None:
        """加载模板文件内容，处理读取异常"""
        try:
            self.content = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"模板文件不存在: {self.path}")
        except PermissionError:
            raise PermissionError(f"无权限读取模板文件: {self.path}")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                "utf-8", b"", 0, 0, 
                f"模板文件 {self.path} 编码不是UTF-8，请检查文件格式"
            )
        except Exception as e:
            raise RuntimeError(f"读取模板文件 {self.path} 失败: {str(e)}") from e
    
    def _extract_placeholders(self) -> List[str]:
        """
        提取并去重占位符（保持原始出现顺序）
        排除固定占位符: modid、modid_safe
        """
        # 匹配 {变量名} 格式，变量名仅包含字母/数字/下划线
        pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
        matches = pattern.findall(self.content)
        
        # 去重且保留原始顺序，排除固定占位符
        seen = set()
        unique_placeholders = []
        for placeholder in matches:
            if (
                placeholder not in seen 
                and placeholder not in {"modid", "modid_safe"}
            ):
                seen.add(placeholder)
                unique_placeholders.append(placeholder)
        
        return unique_placeholders
