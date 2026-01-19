"""
用户界面模块

提供多种交互方式：
- CLI: 命令行模式（默认）
- GUI: Flet 桌面应用（推荐）
"""

from .gui_flet import main as run_flet

__all__ = ["run_flet"]