
import json
from pathlib import Path
from src.model.config import Config

class ConfigDAO:
    """配置数据访问对象：负责加载JSON配置并返回Config模型"""
    
    @staticmethod
    def load(path: str) -> Config:
        """从文件加载配置，自动迁移旧格式"""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with config_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        # 自动迁移旧格式（向后兼容）
        if "tree_types" in raw_data:
            # 将旧格式转换为新格式
            raw_data["replacements"] = [{
                "type": "tree",
                "values": raw_data.pop("tree_types"),
                "extra": raw_data.pop("tree_replacements", {}),
                "enabled": True
            }]
        
        return Config(raw_data)