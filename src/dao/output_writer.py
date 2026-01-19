
import json
from pathlib import Path
from typing import Dict

class OutputWriter:
    """输出写入器：只负责写入文件和统计"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.stats = {"total": 0}
    
    def write(self, filename: str, content: str, dry_run: bool = False) -> Path:
        """写入输出文件"""
        self.stats["total"] += 1
        
        if dry_run:
            return self.output_dir / filename
        
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证JSON格式
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"生成的内容不是有效JSON: {e}")
        
        # 写入文件
        output_path = self.output_dir / filename
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()