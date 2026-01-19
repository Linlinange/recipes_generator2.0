# src/interfaces/gui_flet.py
import flet as ft
from pathlib import Path
import json
import sys

# 将项目根目录加入 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src import RecipeGenerator

class RecipeGeneratorApp:
    def __init__(self):
        self.generator = None
        self.config_path = "config.json"
        self.dry_run = True
        self.explain_mode = False
        self.page = None
        
        # ✅ 在 __init__ 中初始化组件（兼容 Python 3.6+）
        self.log_view = ft.ListView(height=300, spacing=5, expand=True)
        self.stats_text = ft.Text("总数: 0 个文件")
    
    def build(self, page: ft.Page):
        """构建 UI，返回 Column 组件"""
        self.page = page
        
        return ft.Column(
            [  # ✅ 方括号开始
                ft.Text("🎮 MC Recipe Generator", size=30, weight=ft.FontWeight.BOLD),
                
                ft.Row([
                    ft.Text("配置路径:", width=100),
                    ft.TextField(value=self.config_path, width=400, on_change=self.on_config_change),
                ]),
                
                ft.Row([
                    ft.Checkbox(label="预览模式", value=self.dry_run, on_change=self.on_dry_run_change),
                    ft.Checkbox(label="解释模式", on_change=self.on_explain_change),
                ]),
                
                ft.Row([
                    ft.ElevatedButton("🚀 开始生成", on_click=self.on_generate, width=200),
                    ft.ElevatedButton("📁 打开输出目录", on_click=self.open_output, width=200),
                ]),
                
                ft.Text("📋 日志输出:", size=16),
                self.log_view,  # ✅ 直接使用
                
                ft.Text("📊 统计:", size=16),
                self.stats_text,  # ✅ 直接使用
            ],  # ✅ 方括号结束
            spacing=20,
            expand=True,
        )

    def on_config_change(self, e):
        self.config_path = e.control.value
    
    def on_dry_run_change(self, e):
        self.dry_run = e.control.value
    
    def on_explain_change(self, e):
        self.explain_mode = e.control.value
    
    def on_generate(self, e):
        try:
            self.generator = RecipeGenerator(self.config_path)
        except Exception as ex:
            self.log(f"❌ 配置加载失败: {ex}")
            return
        
        import builtins
        old_print = builtins.print
        
        def custom_print(*args, **kwargs):
            msg = " ".join(str(arg) for arg in args)
            self.log(msg)
            old_print(*args, **kwargs)
        
        builtins.print = custom_print
        
        try:
            self.generator.run(dry_run=self.dry_run, explain_mode=self.explain_mode)
            total = self.generator.writer.stats.get("total", 0)
            self.update_stats(total)
        except Exception as ex:
            self.log(f"❌ 生成失败: {ex}")
        finally:
            builtins.print = old_print
    
    def log(self, msg: str):
        self.log_view.controls.append(ft.Text(msg, size=12))
        self.page.update()
    
    def update_stats(self, total: int):
        self.stats_text.value = f"总数: {total} 个文件"
        self.page.update()
    
    def open_output(self, e):
        output_dir = Path("output")
        if output_dir.exists():
            import subprocess
            subprocess.Popen(f'explorer "{output_dir.absolute()}"')
        else:
            self.log("⚠️ 输出目录不存在")

def main():
    def run(page: ft.Page):
        page.title = "MC Recipe Generator"
        page.window_width = 800
        page.window_height = 600
        page.window_resizable = False
        
        app = RecipeGeneratorApp()
        ui = app.build(page)
        page.add(ui)
        page.update()
    
    ft.app(target=run)

if __name__ == "__main__":
    main()