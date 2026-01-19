
import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
sys.path.append(str(Path(__file__).parent))

from src.interfaces.gui_flet import main

if __name__ == "__main__":
    main()