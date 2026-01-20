# src/interfaces/home_page.py
import flet as ft
from typing import Callable
from src.interfaces.base_page import BasePage

class HomePage(BasePage):
   """首页"""
   
   def build(self) -> ft.Control:
       # 创建组件
       welcome_text = self.add_component(
           "welcome_text",
           ft.Text("🏠 MC Recipe Generator", size=30, weight=ft.FontWeight.BOLD)
       )
       
       generator_btn = self.add_component(
           "generator_btn",
           ft.ElevatedButton("开始生成配方 →", width=200, height=50)
       )
       
       localizer_btn = self.add_component(
           "localizer_btn",
           ft.ElevatedButton("开始批量本地化 →", width=200, height=50)
       )
       
       # 组装页面
       return ft.Container(
           content=ft.Column([
               welcome_text,
               ft.Text("欢迎使用Minecraft配方生成工具！", size=16),
               ft.Text("功能特色：", size=18, weight=ft.FontWeight.BOLD),
               ft.Text("• 支持批量生成JSON配方文件"),
               ft.Text("• 灵活的模板占位符替换"),
               ft.Text("• 预览模式避免误操作"),
               ft.Text("• 可视化日志输出"),
               ft.Divider(),
               generator_btn,
               localizer_btn,
           ], expand=True, spacing=20),
           padding=ft.padding.only(top=20)
       )

   # ========== 事件注册方法 ==========
   
   def register_go_generator_event(self, handler: Callable):
       self.register_event("generator_btn", "click", handler)
   
   def register_go_localizer_event(self, handler: Callable):
       self.register_event("localizer_btn", "click", handler)
