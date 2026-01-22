# conftest.py
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

print(f"✅ pytest 已添加项目根目录到 Python 路径: {project_root}")