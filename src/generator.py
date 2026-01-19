
from src.config import ConfigManager
from src.template import Template, TemplateManager
from src.engine import ReplacementEngine, CombinationGenerator
from src.writer import OutputWriter
from pathlib import Path
from typing import Dict, List, Set, Tuple

class RecipeGenerator:
    """主生成器（协调器）"""
    
    def __init__(self, config_path: str):
        """初始化主生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = ConfigManager(config_path)
        self.engine = ReplacementEngine(self.config)
        
        self.writer = OutputWriter(self.config.output_dir)
        self.stats = self.writer.stats
    
    def run(self, dry_run: bool = False, explain_mode: bool = False):
        """运行完整流程"""
        print("\n🚀 开始生成...\n")
        
        templates = self._load_templates()
        
        for template_name, template in templates.items():
            self._process_template(template, dry_run, explain_mode)
        
        self._print_stats()
        
        if dry_run:
            print("⚠️  预览模式，未实际写入文件")
    
    def _load_templates(self) -> Dict[str, Template]:
        """加载模板（辅助方法）"""
        template_dir = self.config.template_dir
        templates = {}
        
        for filename in self.config.get("template_files", []):
            path = template_dir / filename
            if path.exists():
                templates[filename] = Template(path)
            else:
                print(f"⚠️  模板不存在: {path}")
        
        return templates
    
    def _process_template(self, template: Template, dry_run: bool, explain_mode: bool):
        """处理单个模板"""
        combos = self._generate_combinations(template.placeholders)
        
        for combo in combos:
            combo_dict = dict(zip(template.placeholders, combo))
            self._generate_single(template, combo_dict, dry_run, explain_mode)
    
    def _generate_combinations(self, needed_types: Set[str]) -> List[tuple]:
        """生成组合"""
        rules = self.config.get_active_rules()
        return CombinationGenerator.generate(rules, needed_types)
    
    def _generate_single(self, template: Template, combo_dict: Dict, dry_run: bool, explain_mode: bool):
        """生成单个文件"""
        # 对内容应用替换
        explain_log = [] if explain_mode else None
        content = self.engine.apply(template.content, combo_dict, explain_log)
        
        # 生成文件名
        name_parts = [f"{k}_{v.replace(':', '_')}" for k, v in combo_dict.items()]
        filename = "_".join(name_parts) + ".json"
        
        # ✅ 使用 writer 写入（自动更新 stats）
        if dry_run:
            print(f"📄 [预览] {filename}")
        
        self.writer.write(filename, content, dry_run=dry_run)
        
        # 解释模式日志
        if explain_mode and explain_log:
            print(f"\n📝 组合: {combo_dict}")
            for log in explain_log:
                print(log)
    
    def _print_stats(self):
        """打印统计"""
        print(f"\n=== 🎯 生成完成 ===")
        print(f"总数: {self.stats['total']} 个文件")