
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from src.core.localization_engine import LocalizationEngine
from src.dao.batch_item_dao import BatchItemDAO
from src.dao.template_loader import TemplateLoader
from src.dao.config_dao import ConfigDAO
from src.model.batch_item import BatchItem

class LocalizerService:
    """
    本地化服务 - 管理批量本地化生成全流程
    职责：配置管理、BatchItem加载、模板加载、引擎调用、结果输出
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = None
        self.engine: Optional[LocalizationEngine] = None
        self.template_loader: Optional[TemplateLoader] = None
        self.batch_items: Dict[str, BatchItem] = {}
        
        # 回调函数
        self._on_progress: Optional[Callable[[str], None]] = None
        self._on_complete: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None
        
        # 统计信息
        self.stats = {
            "total_items": 0,
            "successful_items": 0,
            "failed_items": 0,
            "total_entries": 0,
            "template_files": 0
        }
    
    def set_callbacks(self, 
                     on_progress: Optional[Callable[[str], None]] = None,
                     on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
                     on_error: Optional[Callable[[Exception], None]] = None):
        """设置回调函数"""
        self._on_progress = on_progress
        self._on_complete = on_complete
        self._on_error = on_error
    
    def _log(self, message: str, is_error: bool = False):
        """内部日志方法"""
        if self._on_progress:
            self._on_progress(message)
        elif is_error:
            print(f"❌ {message}")
        else:
            print(f"ℹ️ {message}")
    
    def reload_config(self) -> bool:
        """
        加载配置文件并初始化所有组件
        返回: 是否成功
        """
        try:
            # 1. 加载配置
            self._log("📄 正在加载配置文件...")
            self.config = ConfigDAO.load(str(self.config_path))
            
            # 2. 加载BatchItems
            self._log("📦 正在加载BatchItem配置...")
            config_dir = self.config_path.parent
            self.batch_items = BatchItemDAO.load(str(config_dir))
            
            # 3. 初始化模板加载器
            self.template_loader = TemplateLoader(self.config.template_dir_path)
            
            # 4. 初始化引擎
            self.engine = LocalizationEngine(
                default_namespace=self.config.default_namespace,
                rules=self.config.rules,
                items=self.batch_items
            )
            
            # 5. 加载模板
            if not self.config.template_files:
                self._log("⚠️ 未配置模板文件，请先添加模板", is_error=True)
                return False
            
            self.engine.load_templates(
                self.config.template_dir_path,
                *self.config.template_files
            )
            
            # 更新统计
            self.stats["template_files"] = len(self.config.template_files)
            self.stats["total_items"] = len(self.batch_items)
            
            self._log(f"✅ 配置加载成功: {self.stats['total_items']} 个物品, {self.stats['template_files']} 个模板")
            return True
            
        except Exception as ex:
            error_msg = f"配置加载失败: {str(ex)}"
            self._log(error_msg, is_error=True)
            if self._on_error:
                self._on_error(ex)
            return False
    
    def start_generation(self, template_name: str, dry_run: bool = False, 
                        explain_mode: bool = False) -> bool:
        """
        启动批量生成流程
        参数:
            template_name: 模板文件名
            dry_run: 预览模式（不写入文件）
            explain_mode: 解释模式（显示详细替换过程）
        返回: 是否成功启动
        """
        if not self.engine or not self.config:
            self._log("❌ 引擎未初始化，请先加载配置", is_error=True)
            return False
        
        if template_name not in self.engine.templates:
            self._log(f"❌ 模板不存在: {template_name}", is_error=True)
            return False
        
        try:
            self._log(f"\n🚀 开始生成: 模板 '{template_name}'")
            if dry_run:
                self._log("👁️  预览模式已启用（不会写入文件）")
            if explain_mode:
                self._log("🔍 解释模式已启用（显示详细替换过程）")
            
            # 重置统计
            self.stats["successful_items"] = 0
            self.stats["failed_items"] = 0
            self.stats["total_entries"] = 0
            
            # 执行生成
            results = self.engine.generate_batch(template_name)
            
            # 处理结果
            if not dry_run:
                self._save_results(results, template_name)
            
            # 更新统计
            self.stats["successful_items"] = len(results)
            self.stats["total_entries"] = sum(len(entries) for entries in results.values())
            
            # 完成回调
            if self._on_complete:
                self._on_complete(self.stats.copy())
            
            return True
            
        except Exception as ex:
            error_msg = f"生成过程出错: {str(ex)}"
            self._log(error_msg, is_error=True)
            if self._on_error:
                self._on_error(ex)
            return False
    
    def _save_results(self, results: Dict[str, Dict[str, str]], template_name: str):
        """保存生成结果到文件"""
        output_dir = self.config.output_dir_path / "localization"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 为每个BatchItem生成独立文件
        for item_id, entries in results.items():
            if not entries:
                continue
            
            # 生成文件名: oak.json, crimson.json 等
            item_key = item_id.split(":")[-1]
            filename = f"{item_key}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            
            self._log(f"  💾 已保存: {filename} ({len(entries)} 条)")
        
        # 生成汇总文件
        summary_file = output_dir / f"_all_{template_name.replace('.json', '')}.json"
        all_entries = {}
        for entries in results.values():
            all_entries.update(entries)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=2)
        
        self._log(f"  📊 汇总文件: {summary_file.name} ({len(all_entries)} 条总计)")
    
    def get_batch_items_by_category(self, category: str = "material") -> List[BatchItem]:
        """按类别获取BatchItem列表"""
        return [item for item in self.batch_items.values() if item.category == category]
    
    def get_available_templates(self) -> List[str]:
        """获取已加载的模板列表"""
        if self.engine and self.engine.templates:
            return list(self.engine.templates.keys())
        return []
    
    def get_output_directory(self) -> str:
        """获取输出目录路径"""
        if self.config:
            return str(self.config.output_dir_path / "localization")
        return "./output/localization"