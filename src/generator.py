# src/generator.py
from src.config import ConfigManager
from src.template import Template
from src.template import TemplateManager
from src.engine import ReplacementEngine, CombinationGenerator
from src.writer import OutputWriter
from pathlib import Path
from typing import Dict, Tuple, List, Set

class RecipeGenerator:
    """主生成器：协调整个流程"""
    
    def __init__(self, config_path: str):
        """初始化主生成器
        
        创建所有依赖组件并初始化统计变量。
        
        Args:
            config_path: 配置文件路径
        """
        # 1. 加载配置
        self.config = ConfigManager(config_path)
        
        # 2. 初始化引擎
        self.engine = ReplacementEngine(self.config)
        
        # 3. ✅ 初始化统计（关键修复）
        self.stats = {"total": 0, "by_type": {}}
    
    def run(self, dry_run: bool = False, explain_mode: bool = False):
        """运行完整生成流程"""
        print("\n🚀 开始生成...\n")
        
        # 加载模板
        templates = self._load_templates()
        
        for template_name, template in templates.items():
            self._process_template(template, dry_run, explain_mode)
        
        # 打印统计
        self._print_stats()
    
    def _load_templates(self) -> Dict[str, 'Template']:
        """加载模板（辅助方法）"""
        # 这里需要导入 Template 类
        from src.template import Template
        
        template_dir = self.config.template_dir
        templates = {}
        
        for filename in self.config.get("template_files", []):
            path = template_dir / filename
            if path.exists():
                templates[filename] = Template(path)
            else:
                print(f"⚠️  模板不存在: {path}")
        
        return templates
    
    def _process_template(self, template: 'Template', dry_run: bool, explain_mode: bool):
        """处理单个模板"""
        combos = self._generate_combinations(template.placeholders)
        
        for combo in combos:
            combo_dict = dict(zip(template.placeholders, combo))
            self._generate_single(template, combo_dict, dry_run, explain_mode)
    
    def _generate_combinations(self, needed_types: Set[str]) -> List[tuple]:
        """生成组合"""
        from src.engine import CombinationGenerator
        
        rules = self.config.get_active_rules()
        return CombinationGenerator.generate(rules, needed_types)
    
    def _generate_single(self, template: 'Template', combo_dict: Dict, 
                         dry_run: bool, explain_mode: bool):
        """生成单个文件（修复版本）"""
        # 获取原始模板文件名
        original_filename = template.path.name
        
        # 对文件名应用替换
        resolved_filename = self.engine.apply(original_filename, combo_dict)
        
        # 处理安全字符
        safe_filename = resolved_filename.replace(":", "_")
        
        # 对内容应用替换
        explain_log = [] if explain_mode else None
        content = self.engine.apply(template.content, combo_dict, explain_log)
        
        # 写入或预览
        if dry_run:
            print(f"📄 [预览] {safe_filename}")
            self.stats["total"] += 1
            return
        
        # 创建目录并写入
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.config.output_dir / safe_filename
        
        try:
            output_path.write_text(content, encoding="utf-8")
            self.stats["total"] += 1
            print(f"✏️  {safe_filename}")
        except Exception as e:
            print(f"❌ 写入失败 {safe_filename}: {e}")
        
        # 解释模式日志
        if explain_mode and explain_log:
            print(f"\n📝 组合: {combo_dict}")
            for log in explain_log:
                print(log)
    
    def _print_stats(self):
        """打印统计"""
        print(f"\n=== 🎯 生成完成 ===")
        print(f"总数: {self.stats['total']} 个文件")
