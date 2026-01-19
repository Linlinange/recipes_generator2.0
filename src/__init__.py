"""
MC Recipe Generator - Minecraft 配方批量生成器

版本: 2.2.0
作者: 林林解说ange
仓库: https://github.com/yourusername/mc-recipe-generator

核心功能:
- 模板驱动：使用 JSON 模板批量生成配方
- 配置即代码：通过 JSON 配置定义替换规则
- 智能命名空间：自动处理 Minecraft 命名空间（minecraft:）
- 额外规则：支持特定值、纯名称、通配符三种匹配
- 预览模式：--dry-run 预览生成结果
- 解释模式：--explain 显示详细替换过程

使用示例:
    from src import RecipeGenerator
    
    generator = RecipeGenerator("config.json")
    generator.run(dry_run=True, explain_mode=True)
"""

__version__ = "2.2.0"
__author__ = "Linlinange"
__email__ = "linlinange@163.com"
__license__ = ""

# 公开 API：导出核心类
from .generator import RecipeGenerator
from .config import ConfigManager
from .template import Template, TemplateManager
from .engine import ReplacementEngine, CombinationGenerator
from .writer import OutputWriter

__all__ = [
    "RecipeGenerator",      # 主生成器
    "ConfigManager",        # 配置管理
    "Template",             # 模板对象
    "TemplateManager",      # 模板管理器
    "ReplacementEngine",    # 替换引擎
    "CombinationGenerator", # 组合生成器
    "OutputWriter",         # 输出写入器
]