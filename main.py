#!/usr/bin/env python3
"""
主入口文件

负责：
1. 解析命令行参数（如 --dry-run）
2. 创建 RecipeGenerator 实例
3. 启动生成流程
"""

from src.generator import RecipeGenerator
import argparse

def main():
    """
    主函数：解析参数并执行生成
    
    支持的命令行参数：
    --dry-run: 预览模式，不写入文件
    --explain: 解释模式（开发中）
    """
    # 创建命令行解析器
    parser = argparse.ArgumentParser(
        description="Minecraft 配方批量生成器 - 配置驱动模板引擎",
        epilog="示例: python main.py --dry-run"
    )
    
    # 添加参数
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="预览模式：只显示将要生成的文件名，不实际写入磁盘"
    )
    
    parser.add_argument(
        "--explain", 
        action="store_true", 
        help="解释模式：显示详细的替换过程（开发中）"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建生成器实例并运行
    # Config 和 ReplacementEngine 会在内部自动创建
    generator = RecipeGenerator("config.json")
    generator.run(dry_run=args.dry_run)

if __name__ == "__main__":
    # 当直接运行此文件时（不是被导入），执行 main()
    main()
