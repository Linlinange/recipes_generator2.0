"""
HomeService - 占位实现
职责：应用元数据、统计数据（功能待扩展）
"""

import sys
from pathlib import Path
from typing import Dict, Any


class HomeService:
    """首页服务（占位实现）"""
    
    def __init__(self):
        
        self.app_name = "MC Recipe Generator"
        self.app_version = "1.2.0"  # 硬编码版本，从pyproject.toml读取的功能待实现
        self.placeholder_stats = {
            "total_generated": 0,
            "template_count": 0,
            "run_count": 0,
        }
    
    # ==================== 占位方法 ====================
    
    def get_app_info(self) -> Dict[str, Any]:
        """获取应用信息（占位）"""
        return {
            "name": self.app_name,
            "version": self.app_version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "flet_version": self._get_flet_version(),
            "status": "running",
        }
    
    def _get_flet_version(self) -> str:
        """获取Flet版本"""
        try:
            import flet
            return flet.__version__
        except Exception:
            return "unknown"
    
    def get_recent_stats(self) -> Dict[str, int]:
        """获取最近统计（占位，以后从日志/文件读取）"""
        # 尝试统计output目录文件数（简单统计）
        try:
            output_dir = Path("./output")
            if output_dir.exists():
                self.placeholder_stats["total_generated"] = len(list(output_dir.glob("*.json")))
            
            template_dir = Path("./templates")
            if template_dir.exists():
                self.placeholder_stats["template_count"] = len(list(template_dir.glob("*.json")))
        except Exception:
            pass
        
        return self.placeholder_stats
    
    def get_welcome_message(self) -> str:
        """获取欢迎消息"""
        return f"欢迎使用 {self.app_name} v{self.app_version}！"