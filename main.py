#!/usr/bin/env python3
"""
主入口：CLI + Flet GUI 双模式
"""

from src import RecipeGenerator
from src.interfaces.gui_flet import main as run_flet
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="MC Recipe Generator - CLI + Flet GUI",
        epilog="示例: python main.py --ui flet  # 启动桌面应用"
    )
    
    parser.add_argument(
        "--ui", 
        choices=["cli", "flet"], 
        default="cli", 
        help="界面模式: cli(命令行) / flet(桌面应用)"
    )
    
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--explain", action="store_true", help="解释模式")
    
    args = parser.parse_args()
    
    if args.ui == "flet":
        # ✅ 启动 Flet 桌面应用
        run_flet()
    else:
        # CLI 模式
        generator = RecipeGenerator("config.json")
        generator.run(dry_run=args.dry_run, explain_mode=args.explain)

if __name__ == "__main__":
    main()