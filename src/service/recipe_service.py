# src/service/recipe_service.py

"""
RecipeService - 配方生成服务（架构图中的GeneratorService）
职责：调用多个DAO，协调生成全流程，不依赖其他Service
"""

import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Tuple
from io import StringIO

from src.model.config import Config
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader
from src.dao.output_writer import OutputWriter
from src.core.engine import ReplacementEngine
from src.service.settings_service import SettingsService


class RecipeService:
    """配方生成服务"""
    
    def __init__(self, settings_service: Optional['SettingsService'] = None):

        # 依赖注入
        self.settings_service = settings_service
        
        # 业务组件（执行者）
        self.config: Optional[Config] = None
        self.engine: Optional[ReplacementEngine] = None
        self.template_loader: Optional[TemplateLoader] = None
        self.output_writer: Optional[OutputWriter] = None
        
        # 业务状态（生成任务的生命周期）
        self._is_running = False          # 任务是否在运行
        self._cancel_requested = False    # 用户是否请求取消
        self._processed_count = 0         # 已处理数量
        self._current_template_name = ""  # 当前模板名
        self._total_templates = 0         # 总模板数
        
        # 业务回调（通知外部状态变化）
        self.on_progress: Optional[Callable[[str], None]] = None
        self.on_complete: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        # 如果提供了SettingsService，立即加载配置
        if settings_service:
            self.reload_config()
        
        # ... 其他初始化代码 ...
        # 待完善
    
    # ==================== 公共API（供Page调用） ====================
    
    def reload_config(self) -> bool:
        """从SettingsService重新加载配置"""
        if not self.settings_service:
            print("❌ 未配置SettingsService")
            return False
        
        try:
            config_dict = self.settings_service.get_config_dict()
            if not config_dict:
                print("⚠️  配置为空")
                return False
            
            self.config = Config.from_dict(config_dict)
            self._initialize_components()
            self._log("✅ 配置已从SettingsService同步")
            return True
        except Exception as ex:
            print(f"❌ 从SettingsService加载配置失败: {ex}")
            return False
    
    def load_config_from_file(self, config_path: str = "config.json") -> bool:
        """从文件加载配置（备用方法）"""
        try:
            self.config = ConfigDAO.load(config_path)
            self._initialize_components()
            return True
        except Exception as ex:
            print(f"❌ 加载配置文件失败: {ex}")
            return False
    
    def start_generation(self, dry_run: bool = False, explain_mode: bool = False) -> bool:
        """
        开始生成配方（核心方法）
        参数:
            dry_run: 预览模式
            explain_mode: 解释模式
        返回:
            是否成功启动
        """
        if self._is_running:
            self._log("⚠️ 任务已在运行中")
            return False
        
        if not self.config or not self.config.template_files:
            self._log("❌ 未加载配置或未选择模板")
            return False
        
        # 重置状态
        self._is_running = True
        self._cancel_requested = False
        self._processed_count = 0
        self._current_template_name = ""
        self._total_templates = len(self.config.template_files)
        
        # 在后台线程执行
        thread = threading.Thread(
            target=self._run_internal,
            args=(dry_run, explain_mode),
            daemon=True
        )
        thread.start()
        
        return True
    
    def cancel_generation(self):
        """取消生成"""
        self._cancel_requested = True
        self._log("🛑 正在取消任务...")
    
    @property
    def is_running(self) -> bool:
        """查询运行状态"""
        return self._is_running
    
    @property
    def status(self) -> Dict[str, Any]:
        """获取完整状态信息"""
        progress = 0.0
        if self._total_templates > 0:
            processed_templates = self._processed_count // max(total_combinations := 1, 1)
            progress = (processed_templates / self._total_templates) * 100
        
        return {
            "is_running": self._is_running,
            "progress": round(progress, 2),
            "processed_count": self._processed_count,
            "current_template": self._current_template_name,
            "total_templates": self._total_templates,
        }
    
    def set_callbacks(
        self,
        on_progress: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """设置回调函数（供Page注入）"""
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
    
    def preview_combinations(self, limit: int = 5) -> List[Tuple[str, str]]:
        """
        预览组合（调用多个DAO）
        参数:
            limit: 预览数量限制
        返回:
            (文件名, 内容)列表
        """
        if not self.config or not self.config.template_files:
            return []
        
        try:
            # 调用DAO直接加载模板
            templates = self.template_loader.load_all(self.config.template_files[:1])
            if not templates:
                return []
            
            # 生成预览
            previews = []
            first_template = list(templates.values())[0]
            combos = self.engine.generate_combinations(first_template)
            
            for combo in combos[:limit]:
                # 生成文件名
                filename = self.engine.apply(first_template.path.name, combo, None)
                filename = filename.replace(":", "_")
                
                # 生成内容
                explain_log = []  # 预览时不需要解释
                content = self.engine.apply(first_template.content, combo, explain_log)
                
                # 格式化内容
                try:
                    data = json.loads(content)
                    formatted = json.dumps(data, ensure_ascii=False, indent=2)
                except:
                    formatted = content
                
                previews.append((filename, formatted))
            
            return previews
            
        except Exception as ex:
            self._log(f"预览失败: {ex}", is_error=True)
            return []
    
    def get_output_directory(self) -> str:
        """获取当前输出目录"""
        return self.config.output_dir if self.config else "./output"
    
    # ==================== 内部实现 ====================
    
    def _run_internal(self, dry_run: bool, explain_mode: bool):
        """内部同步执行（在后台线程）"""
        try:
            self._log("\n🚀 开始生成配方...")
            
            # 1. 调用DAO加载模板
            templates = self.template_loader.load_all(self.config.template_files)
            if not templates:
                self._log("⚠️  没有可用的模板，请检查配置。")
                return
            
            self._log(f"📂 加载了 {len(templates)} 个模板")
            
            # 2. 处理每个模板
            for filename, template in templates.items():
                if self._cancel_requested:
                    self._log("\n🛑 任务已取消")
                    break
                
                self._current_template_name = filename
                self._process_template(template, dry_run, explain_mode)
                self._processed_count += 1
            
            # 3. 完成统计
            if not self._cancel_requested:
                stats = self.output_writer.get_stats()
                self._log(f"\n" + "="*50)
                self._log(f"🎯 生成完成")
                self._log(f"   总计: {stats['total']} 个文件")
                self._log("="*50)
                
                if dry_run:
                    self._log("\n⚠️  预览模式，未实际写入文件")
                
                if self.on_complete:
                    self.on_complete(stats)
                
        except Exception as e:
            self._log(f"\n❌ 错误: {e}", is_error=True)
            if self.on_error:
                self.on_error(e)
        finally:
            self._is_running = False
            self._current_template_name = ""
    
    def _process_template(self, template, dry_run: bool, explain_mode: bool):
        """处理单个模板"""
        self._log(f"\n📄 处理模板: {template.path.name}")
        
        # 调用Engine生成组合
        combos = self.engine.generate_combinations(template)
        
        if not combos:
            self._log(f"   ⚠️  没有生成任何组合")
            return
        
        self._log(f"   生成 {len(combos)} 个组合")
        
        # 处理每个组合
        for combo in combos:
            if self._cancel_requested:
                break
            
            # 生成文件名和内容
            filename = self.engine.apply(template.path.name, combo, None)
            filename = filename.replace(":", "_").replace("/", "_").replace("\\", "_")
            
            explain_log = [] if explain_mode else None
            content = self.engine.apply(template.content, combo, explain_log)
            
            # 调用DAO写入文件
            self.output_writer.write(filename, content, dry_run)
            self._processed_count += 1
            self._log(f"   📄 {'[预览] ' if dry_run else ''}{filename}")
            
            # 解释模式日志
            if explain_log:
                self._log(f"\n   📝 组合详情: {combo}")
                for log in explain_log:
                    self._log(f"      {log}")
    
    def _initialize_components(self):
        """初始化核心组件"""
        if not self.config:
            return
        
        # 调用DAO创建组件
        self.engine = ReplacementEngine(self.config.default_namespace, self.config.rules)
        self.template_loader = TemplateLoader(Path(self.config.template_dir))
        self.output_writer = OutputWriter(Path(self.config.output_dir))
    
    def _log(self, message: str, is_error: bool = False):
        """日志输出（带回调）"""
        callback = getattr(self, 'on_progress', None)
        if callback:
            callback(message)
        else:
            print(message)
    
    def _get_default_config(self) -> Config:
        """获取默认配置"""
        return Config({
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        })
    