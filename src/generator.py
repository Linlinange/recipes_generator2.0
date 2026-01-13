# src/generator.py
from src.config import ConfigManager
from src.template import TemplateManager
from src.engine import ReplacementEngine, CombinationGenerator
from src.writer import OutputWriter
from pathlib import Path
from typing import Dict, Tuple

class RecipeGenerator:
    """
    主生成器（Facade 模式）
    职责：协调所有组件，执行完整流程
    对应原函数：main() 的执行逻辑
    """
    
    def __init__(self, config_path: str):
        # 1. 加载配置
        self.config = ConfigManager(config_path)
        
        # 2. 初始化组件
        self.template_manager = TemplateManager(self.config.template_dir)
        self.engine = ReplacementEngine(self.config)
        self.writer = OutputWriter(self.config.output_dir)
    
    def run(self, dry_run: bool = False, explain_mode: bool = False):
        """运行完整流程"""
        print("\n🚀 开始生成...\n")
        
        # 加载模板
        templates = self.template_manager.load_all(
            self.config.get("template_files", [])
        )
        
        for template_name, template in templates.items():
            self._process_template(template, dry_run, explain_mode)
        
        # 打印统计
        self.writer.print_stats()
        
        if dry_run:
            print("⚠️  预览模式，未实际写入文件")
    
    def _process_template(self, template, dry_run: bool, explain_mode: bool):
        """处理单个模板"""
        # 生成组合
        combos = CombinationGenerator.generate(
            self.config.get_active_rules(),
            template.placeholders
        )
        
        for combo_tuple in combos:
            combo_dict = dict(zip(template.placeholders, combo_tuple))
            self._generate_single(template, combo_dict, dry_run, explain_mode)
    
    def _generate_single(self, template, combo: Dict, dry_run: bool, explain_mode: bool):
        """生成单个文件"""
        # 1. 应用替换
        explain_log = [] if explain_mode else None
        content = self.engine.apply(template.content, combo, explain_log)
        
        # 2. 生成文件名
        name_parts = [f"{k}_{v.replace(':', '_')}" for k, v in combo.items()]
        filename = "_".join(name_parts) + ".json"
        
        # 3. 写入
        self.writer.write(filename, content, dry_run)
        
        # 4. 解释模式输出
        if explain_mode:
            print(f"\n📝 组合: {combo}")
            for log in explain_log or []:
                print(log)
