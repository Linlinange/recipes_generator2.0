import json
from pathlib import Path
from typing import Dict, List, Any
from src.model.batch_item import BatchItem

class BatchItemDAO:
    """
    批量生成项数据访问对象
    职责: 加载和保存 batch_items.json 配置
    设计: 与ConfigDAO保持一致的异常处理和API风格
    """
    
    DEFAULT_FILENAME = "batch_items.json"
    
    @staticmethod
    def load(config_dir: str, filename: str = None) -> Dict[str, BatchItem]:
        """
        从配置目录加载BatchItem列表
        
        参数:
            config_dir: 配置文件所在目录
            filename: 文件名，默认为 batch_items.json
        
        返回:
            Dict[str, BatchItem]: 以item.id为键的字典
            
        异常:
            FileNotFoundError: batch_items.json不存在
            json.JSONDecodeError: JSON格式错误
            KeyError: 缺少必要的'items'字段
            ValueError: 单个item解析失败
        """
        items_path = Path(config_dir) / (filename or BatchItemDAO.DEFAULT_FILENAME)
        
        # 文件存在性检查
        if not items_path.exists():
            raise FileNotFoundError(
                f"批量生成项配置文件不存在: {items_path}\n"
                f"请确保在配置目录下创建 '{BatchItemDAO.DEFAULT_FILENAME}'，格式:\n"
                f'{{"items": [{{"id": "...", "zh_cn": "...", "namespace": "..."}}]}}'
            )
        
        # 加载JSON（含异常处理）
        try:
            with items_path.open('r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"BatchItem配置文件JSON解析失败: {items_path}\n错误: {str(e)}",
                e.doc, e.pos
            ) from None
        
        # 数据结构验证
        if "items" not in raw_data:
            raise KeyError(
                f"BatchItem配置文件缺少 'items' 字段: {items_path}\n"
                f"请确保根节点包含 'items': [] 数组"
            )
        
        if not isinstance(raw_data["items"], list):
            raise TypeError(
                f"BatchItem配置 'items' 必须是列表: {items_path}\n"
                f"当前类型: {type(raw_data['items'])}"
            )
        
        # 转换为BatchItem对象
        items_dict = {}
        for idx, item_data in enumerate(raw_data["items"]):
            try:
                # 验证必需字段
                if "id" not in item_data or "zh_cn" not in item_data:
                    raise ValueError(f"缺少必需字段 'id' 或 'zh_cn'")
                
                item = BatchItem.create(item_data)
                items_dict[item.id] = item
                
            except (TypeError, KeyError, ValueError) as e:
                # 包装错误信息，包含索引和数据
                raise ValueError(
                    f"BatchItem配置第 {idx+1} 项解析失败: {str(e)}\n"
                    f"数据内容: {item_data}\n"
                    f"文件路径: {items_path}"
                ) from e
        
        return items_dict
    
    @staticmethod
    def save(items: Dict[str, BatchItem], config_dir: str, 
             filename: str = None) -> bool:
        """
        保存BatchItem配置到文件（后续扩展用，如GUI编辑器）
        
        参数:
            items: BatchItem字典
            config_dir: 配置目录
            filename: 文件名（默认 batch_items.json）
        
        返回:
            bool: 是否成功保存
        """
        try:
            items_path = Path(config_dir) / (filename or BatchItemDAO.DEFAULT_FILENAME)
            items_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 序列化为标准格式
            data = {
                "items": [item.to_dict() for item in items.values()]
            }
            
            # 写入文件（格式化，中文正常显示）
            with items_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return True
        
        except (IOError, TypeError) as e:
            print(f"❌ 保存BatchItem配置失败: {str(e)}\n路径: {items_path}")
            return False
    
    @staticmethod
    def validate_items(items: Dict[str, BatchItem]) -> List[str]:
        """
        验证BatchItem配置的有效性（后续扩展用）
        
        返回:
            错误信息列表，空列表表示全部有效
        """
        errors = []
        for item_id, item in items.items():
            if not item.zh_cn.strip():
                errors.append(f"项 '{item_id}' 的中文名不能为空")
            if ":" in item.id and not item.namespace:
                errors.append(f"项 '{item_id}' 有命名空间但namespace字段为空")
        return errors
    
    @staticmethod
    def get_material_groups(items: Dict[str, BatchItem]) -> Dict[str, List[BatchItem]]:
        """
        按 category 字段分组 BatchItem
        
        参数:
            items: BatchItem 字典
            
        返回:
            Dict[str, List[BatchItem]]: 分组后的字典
            示例: {"material": [BatchItem(...), ...], "tool": [...]}
        """
        groups = {}
        for item in items.values():
            category = item.category
            if category not in groups:
                groups[category] = []
            groups[category].append(item)
        
        # 按 id 排序保持稳定性
        return {k: sorted(v, key=lambda x: x.id) for k, v in groups.items()}