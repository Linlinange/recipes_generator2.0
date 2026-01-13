# src/writer.py
import json
from pathlib import Path
from typing import Dict

class OutputWriter:
    """
    输出写入器
    职责：写入文件 + 统计信息
    对应原函数：write_output_file() + 统计逻辑
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.stats = {"total": 0, "by_type": {}}
    
    def write(self, filename: str, content: str, dry_run: bool = False) -> Path:
        """
        写入文件
        
        Args:
            filename: 文件名（已替换占位符）
            content: JSON 内容
            dry_run: 预览模式
        
        Returns:
            输出文件路径
        """
        if dry_run:
            self.stats["total"] += 1
            return self.output_dir / filename
        
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证并格式化 JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"生成的内容不是有效 JSON")
        
        # 写入文件
        output_path = self.output_dir / filename
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stats["total"] += 1
        return output_path
    
    def print_stats(self):
        """打印统计"""
        print(f"\n=== 🎯 生成完成 ===")
        print(f"总数: {self.stats['total']} 个文件")
