
import sys
from pathlib import Path
from src.service.recipe_service import RecipeService  # ✅ 更新导入

def main():
    # 配置路径（默认或命令行参数）
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    try:
        # ✅ 更新：使用 RecipeService
        service = RecipeService(config_path)
        service.run(dry_run=False, explain_mode=False)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()