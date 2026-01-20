
from pathlib import Path
from typing import Dict, List
from src.model.template import Template

class TemplateLoader:
    """模板加载器：只负责从磁盘加载模板文件"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self._validate_directory()
    
    def _validate_directory(self) -> None:
        """验证模板目录的合法性（存在+可访问）"""
        if not self.template_dir.exists():
            raise FileNotFoundError(f"模板目录不存在: {self.template_dir}")
        if not self.template_dir.is_dir():
            raise NotADirectoryError(f"指定路径不是目录: {self.template_dir}")
        if not self._is_directory_accessible():
            raise PermissionError(f"无访问权限: {self.template_dir}")
    
    def _is_directory_accessible(self) -> bool:
        """检查目录是否可读写"""
        try:
            # 尝试创建临时文件/读取目录来验证权限
            test_file = self.template_dir / ".permission_test"
            test_file.touch(exist_ok=True)
            test_file.unlink()
            return True
        except PermissionError:
            return False
    
    def load_all(self, filenames: List[str]) -> Dict[str, Template]:
        """批量加载模板"""
        templates = {}
        for name in filenames:
            path = self.template_dir / name
            try:
                templates[name] = Template(path)
            except FileNotFoundError:
                print(f"⚠️  模板不存在: {path}")
            except (PermissionError, UnicodeDecodeError) as e:
                print(f"❌ 加载模板失败 {path}: {str(e)}")
        return templates
    
    def load_single(self, filename: str) -> Template:
        """加载单个模板"""
        path = self.template_dir / filename
        try:
            return Template(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"模板不存在: {path}")
        except (PermissionError, UnicodeDecodeError) as e:
            raise RuntimeError(f"加载模板 {path} 失败: {str(e)}") from e
    
    @staticmethod
    def scan_directory(directory: Path) -> List[Path]:
        """
        扫描指定目录下所有 *.json 模板文件
        参数: 模板目录的Path对象
        返回: 该目录下所有 *.json 文件的Path列表（按文件名排序）
        备注: 处理目录不存在、无权限等异常
        """
        try:
            # 验证目录合法性
            if not directory.exists():
                raise FileNotFoundError(f"扫描目录不存在: {directory}")
            if not directory.is_dir():
                raise NotADirectoryError(f"扫描路径不是目录: {directory}")
            
            # 遍历所有.json文件并按文件名排序
            json_files = sorted(
                directory.glob("*.json"),
                key=lambda p: p.name.lower()  # 不区分大小写排序
            )
            return json_files
        
        except PermissionError as e:
            print(f"❌ 无权限访问扫描目录: {directory}, 错误: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ 扫描目录 {directory} 时发生未知错误: {str(e)}")
            return []
