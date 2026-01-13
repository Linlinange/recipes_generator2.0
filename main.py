#!/usr/bin/env python3
"""
主入口：CLI 参数解析 + 启动生成器
"""

from src.generator import RecipeGenerator
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Minecraft 配方批量生成器 - OO 重构版",
        epilog="示例: python main.py --dry-run --explain"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="预览模式：不写入文件"
    )
    
    parser.add_argument(
        "--explain", 
        action="store_true", 
        help="解释模式：显示详细替换过程"
    )
    
    args = parser.parse_args()
    
    # 创建并运行生成器
    generator = RecipeGenerator("config.json")
    generator.run(dry_run=args.dry_run, explain_mode=args.explain)

if __name__ == "__main__":
    main()
