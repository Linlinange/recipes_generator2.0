
from pathlib import Path
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader
from src.dao.output_writer import OutputWriter
from src.core.engine import ReplacementEngine

class RecipeService:
    """服务层：协调整个配方生成业务流程"""
    
    def __init__(self, config_path: str):
        """
        初始化服务，依赖注入所有组件
        """
        # 1. 加载配置 (DAO)
        self.config = ConfigDAO.load(config_path)
        
        # 2. 初始化核心引擎 (Core)
        self.engine = ReplacementEngine(
            self.config.default_namespace,
            self.config.rules
        )
        
        # 3. 初始化数据访问对象 (DAO)
        self.template_loader = TemplateLoader(
            Path(self.config.template_dir)
        )
        self.output_writer = OutputWriter(
            Path(self.config.output_dir)
        )
    
    def run(self, dry_run: bool = False, explain_mode: bool = False):
        """执行完整的生成流程"""
        print("\n🚀 开始生成配方...\n")
        
        # 1. 加载模板
        templates = self.template_loader.load_all(self.config.template_files)
        if not templates:
            print("⚠️  没有可用的模板，请检查配置。")
            return
        
        print(f"📂 加载了 {len(templates)} 个模板")
        
        # 2. 处理每个模板
        for filename, template in templates.items():
            self._process_template(template, dry_run, explain_mode)
        
        # 3. 打印统计
        self._print_stats()
        
        # 4. 预览模式提示
        if dry_run:
            print("\n⚠️  预览模式，未实际写入文件")
    
    def _process_template(self, template, dry_run: bool, explain_mode: bool):
        """处理单个模板的所有组合"""
        print(f"\n📄 处理模板: {template.path.name}")
        
        # 生成所有组合
        combos = self.engine.generate_combinations(template)
        
        if not combos:
            print(f"   ⚠️  没有生成任何组合")
            return
        
        print(f"   生成 {len(combos)} 个组合")
        
        # 处理每个组合
        for combo in combos:
            self._process_combination(template, combo, dry_run, explain_mode)
    
    def _process_combination(self, template, combo: dict, dry_run: bool, explain: bool):
        """处理单个组合"""
        # 1. 生成文件名
        filename = self.engine.apply(template.path.name, combo, None)
        filename = filename.replace(":", "_")
        
        # 2. 生成内容
        explain_log = [] if explain else None
        content = self.engine.apply(template.content, combo, explain_log)
        
        # 3. 写入文件
        if dry_run:
            print(f"   📄 [预览] {filename}")
        
        self.output_writer.write(filename, content, dry_run)
        
        # 4. 解释模式输出
        if explain_log:
            print(f"\n   📝 组合详情: {combo}")
            for log in explain_log:
                print(f"      {log}")
    
    def _print_stats(self):
        """打印生成统计"""
        stats = self.output_writer.get_stats()
        print(f"\n" + "=" * 50)
        print(f"🎯 生成完成")
        print(f"   总计: {stats['total']} 个文件")
        print("=" * 50)