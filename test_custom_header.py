# test_custom_header.py
import flet as ft

class MultiPageApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_page = "home"  # 记录当前页面
        
        # 创建所有页面（初始隐藏）
        self.pages = {
            "home": self._build_home_page(),
            "generator": self._build_generator_page(),
            "settings": self._build_settings_page(),
        }
        
        # 创建Header
        self.header = self._build_header()
        
        # 初始显示首页
        self.content_area = ft.Container(
            content=self.pages["home"],
            expand=True,  # 填充剩余空间
        )
        
        # 组装
        page.add(
            ft.Column([
                self.header,      # 固定Header
                self.content_area, # 动态内容区
            ], expand=True, spacing=0)
        )
    
    def _build_header(self):
        """构建自定义导航栏"""
        return ft.Container(
            content=ft.Row([
                self._nav_button("首页", "home", ft.icons.HOME),
                self._nav_button("生成器", "generator", ft.icons.BUILD),
                self._nav_button("设置", "settings", ft.icons.SETTINGS),
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.BLUE_GREY_900,
            padding=10,
        )
    
    def _nav_button(self, text, page_name, icon):
        """创建导航按钮"""
        # 判断是否是当前页面，高亮显示
        is_active = self.current_page == page_name
        
        return ft.TextButton(
            content=ft.Row([
                ft.Icon(icon, color="white"),
                ft.Text(text, color="white"),
            ], spacing=5),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE if is_active else "transparent",
            ),
            on_click=lambda e: self._switch_page(page_name),
        )
    
    def _switch_page(self, page_name):
        """切换页面"""
        if self.current_page == page_name:
            return
        
        # 更新状态
        self.current_page = page_name
        
        # 切换内容（淡入淡出动画）
        self.content_area.content = ft.AnimatedSwitcher(
            self.pages[page_name],
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
        )
        
        # 更新Header高亮
        self.header.content = self._build_header().content
        
        self.page.update()
    
    def _build_home_page(self):
        return ft.Column([
            ft.Text("🏠 首页", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("这是首页内容"),
        ], expand=True)
    
    def _build_generator_page(self):
        return ft.Column([
            ft.Text("⚙️ 生成器", size=30, weight=ft.FontWeight.BOLD),
            ft.TextField(label="配置路径", expand=True),
            ft.Row([
                ft.Checkbox(label="预览模式"),
                ft.Checkbox(label="解释模式"),
            ]),
            ft.ElevatedButton("开始", expand=True),
        ], expand=True, spacing=20)
    
    def _build_settings_page(self):
        return ft.Column([
            ft.Text("⚙️ 设置", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("这里是设置页面"),
        ], expand=True)

def main(page: ft.Page):
    page.title = "自定义Header应用"
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    
    app = MultiPageApp(page)

ft.app(target=main)