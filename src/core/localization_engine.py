import json
from pathlib import Path
from typing import Dict, List, Tuple
from src.core.engine import ReplacementEngine
from src.model.template import Template
from src.model.batch_item import BatchItem
from src.dao.batch_item_dao import BatchItemDAO

class LocalizationEngine(ReplacementEngine):
    """
    本地化专用引擎 - 支持BatchItem配置和模板处理
    职责: 将BatchItem + Template → 真实本地化条目
    """
    
    def __init__(self, default_namespace: str, rules: List, items: Dict[str, BatchItem]):
        """
        参数:
            default_namespace: 默认命名空间
            rules: 通用替换规则（复用父类）
            items: BatchItem字典（核心数据载体）
        """
        super().__init__(default_namespace, rules)
        self.items = items  # 类型: Dict[str, BatchItem]
        self.templates: Dict[str, Template] = {}
    
    def load_templates(self, template_dir: Path, *filenames: str):
        """
        加载并解析多个模板文件
        
        参数:
            template_dir: 模板目录
            *filenames: 可变参数，支持加载多个模板
        
        处理逻辑：
        - .json 文件：解析为字典
        - .txt / .template 文件：保持为字符串
        - 其他：保持为字符串
        """
        for filename in filenames:
            path = template_dir / filename
            
            # 1. 加载原始内容
            base_template = Template(path)
            
            # 2. 根据扩展名解析
            template = Template(path)  # 创建新实例用于存储解析后内容
            template.placeholders = base_template.placeholders  # 复用提取的占位符
            
            if filename.endswith('.json'):
                # JSON 格式：解析为字典
                template.content = json.loads(base_template.content)
            else:
                # 其他格式：保持字符串
                template.content = base_template.content
            
            self.templates[filename] = template
            print(f"📄 加载模板: {filename} ({type(template.content).__name__})")
    
    def generate_for_item(self, item_id: str, template_name: str) -> Tuple[str, Dict[str, str]]:
        """
        为单个BatchItem生成完整条目
        
        返回:
            (item_id: str, entries: Dict[str, str])
            如: ("minecraft:oak", {"block.pfm.oak_chair": "基本橡木椅子", ...})
        """
        # 获取BatchItem和Template
        item = self.items.get(item_id)
        if not item:
            raise KeyError(f"BatchItem不存在: {item_id}")
        
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"模板未加载: {template_name}")
        
        # 生成条目
        entries = {}
        for key_template, value_template in template.content.items():
            # 跳过被filter的模板
            if item.should_skip_template(key_template):
                continue
            
            # 生成真实键名
            real_key = self._build_real_key(key_template, item)
            
            # 生成值：基础替换 + 后处理
            combo = self._build_combo(item)
            real_value = self.apply(value_template, combo)
            real_value = item.apply_replacements(real_value)
            
            entries[real_key] = real_value
        
        return item_id, entries
    
    def _build_combo(self, item: BatchItem) -> Dict[str, str]:
        """为apply()构建替换参数组合"""
        return {
            "material_id": item.get_key_prefix(),
            "material_zh_cn": item.zh_cn,
            "modid_safe": item.get_modid_safe(),
            "category": item.category
        }
    
    def _build_real_key(self, key_template: str, item: BatchItem) -> str:
        """
        构建真实键名（处理占位符、特殊转换、清理）
        
        示例:
            "block.pfm.{material_id}_chair" → "block.pfm.oak_chair"
            "block.pfm.stripped_{material_id}_log" → "block.pfm.stripped_crimson_stem"
        """
        real_key = key_template
        
        # 1. 替换标准占位符
        real_key = real_key.replace("{material_id}", item.get_key_prefix())
        real_key = real_key.replace("{modid_safe}", item.get_modid_safe())
        real_key = real_key.replace("{category}", item.category)
        
        # 2. 特殊处理：crimson/warped 的 log → stem
        if item.id in ["minecraft:crimson", "minecraft:warped"]:
            real_key = real_key.replace("_log_", "_stem_")
            real_key = real_key.replace("table_log", "table_stem")
        
        # 3. 清理连续下划线
        while "__" in real_key:
            real_key = real_key.replace("__", "_")
        
        # 4. 移除首尾下划线
        return real_key.strip('_')
    
    def generate_batch(self, template_name: str) -> Dict[str, Dict[str, str]]:
        """
        批量生成所有BatchItem的条目
        
        返回:
            {
                "minecraft:oak": {"block.pfm.oak_chair": "...", ...},
                "minecraft:crimson": {"block.pfm.crimson_chair": "...", ...},
                ...
            }
        """
        results = {}
        for item_id in self.items.keys():
            try:
                item_id_result, entries = self.generate_for_item(item_id, template_name)
                results[item_id_result] = entries
                print(f"✅ 生成成功: {item_id_result} ({len(entries)} 条)")
            except Exception as e:
                print(f"❌ 生成失败: {item_id}\n错误: {str(e)}")
                # 继续生成其他项，不中断整个流程
                continue
        
        return results