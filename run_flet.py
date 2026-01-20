from pathlib import Path
import sys
import flet as ft
import json

sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage
from src.service.recipe_service import RecipeService
from src.dao.config_dao import ConfigDAO

# ========== 首页事件处理器 ==========

def create_go_generator_handler(router):
    """创建跳转到生成器页面的事件处理器"""
    def handler(e):
        router.go("generator")
    return handler

def create_go_localizer_handler(router):
    """创建跳转到本地化页面的事件处理器"""
    def handler(e):
        router.go("localizer")
    return handler

# ========== 生成器页面事件处理器 ==========

def create_dry_run_handler(generator_page):
    """创建预览模式切换事件处理器"""
    def handler(e):
        log_view = generator_page.get_component("log_view")
        is_checked = e.control.value
        
        if log_view:
            if is_checked:
                log_view.controls.append(
                    ft.Text("ℹ️ 预览模式已启用（不会实际写入文件）", color="grey", size=12)
                )
            else:
                log_view.controls.append(
                    ft.Text("⚠️ 预览模式已关闭（会实际写入文件）", color="red", size=12)
                )
            log_view.update()
    
    return handler

def create_explain_handler(generator_page):
    """创建解释模式切换事件处理器"""
    def handler(e):
        log_view = generator_page.get_component("log_view")
        is_checked = e.control.value
        
        if log_view:
            if is_checked:
                log_view.controls.append(
                    ft.Text("💡 解释模式已启用（将显示详细替换过程）", color="blue", size=12)
                )
            log_view.update()
    
    return handler

def create_generator_handler(generator_page):
    """创建开始生成按钮的事件处理器"""
    def handler(e):
        # 获取组件
        log_view = generator_page.get_component("log_view")
        stats_container = generator_page.get_component("stats_container")
        generate_btn = generator_page.get_component("generate_btn")
        config_field = generator_page.get_component("config_field")
        dry_run_checkbox = generator_page.get_component("dry_run_checkbox")
        explain_checkbox = generator_page.get_component("explain_checkbox")
        
        if not all([log_view, stats_container, generate_btn, config_field]):
            print("❌ 组件未正确初始化")
            return
        
        # 1. 初始化UI状态
        log_view.controls.clear()
        stats_container.content = ft.Text("总数: 0 个文件", size=14, weight=ft.FontWeight.BOLD)
        generate_btn.disabled = True
        generate_btn.text = "生成中..."
        generate_btn.update()
        
        try:
            # 2. 获取用户输入
            config_path = config_field.value
            dry_run = dry_run_checkbox.value if dry_run_checkbox else True
            explain_mode = explain_checkbox.value if explain_checkbox else False
            
            # 3. 创建服务
            service = RecipeService(config_path)
            
            # 4. 重定向print到日志
            import builtins
            old_print = builtins.print
            
            def custom_print(*args, **kwargs):
                msg = " ".join(str(arg) for arg in args)
                if log_view:
                    log_view.controls.append(ft.Text(msg, size=12))
                    log_view.update()
                old_print(*args, **kwargs)
            
            builtins.print = custom_print
            
            # 5. 运行生成
            service.run(dry_run=dry_run, explain_mode=explain_mode)
            
            # 6. 更新统计
            stats = service.output_writer.get_stats()
            stats_container.content = ft.Text(
                f"总数: {stats['total']} 个文件",
                size=14,
                weight=ft.FontWeight.BOLD
            )
            
            # 7. 恢复print
            builtins.print = old_print
            
        except Exception as ex:
            if log_view:
                log_view.controls.append(
                    ft.Text(f"❌ 错误: {ex}", color="red", size=14)
                )
                log_view.update()
        
        finally:
            # 8. 恢复按钮
            generate_btn.disabled = False
            generate_btn.text = "🚀 开始生成"
            generate_btn.update()
    
    return handler

def create_generator_open_handler(generator_page):
    """创建打开目录按钮的事件处理器"""
    def handler(e):
        log_view = generator_page.get_component("log_view")
        config_field = generator_page.get_component("config_field")
        
        try:
            config = ConfigDAO.load(config_field.value or "config.json")
            output_dir = Path(config.output_dir)
            
            if output_dir.exists():
                import subprocess
                subprocess.Popen(f'explorer "{output_dir.absolute()}"')
                if log_view:
                    log_view.controls.append(
                        ft.Text(f"📂 已打开目录: {output_dir}", color="orange", size=12)
                    )
                    log_view.update()
            else:
                if log_view:
                    log_view.controls.append(
                        ft.Text("⚠️ 输出目录不存在", color="orange", size=12)
                    )
                    log_view.update()
            
        except Exception as ex:
            if log_view:
                log_view.controls.append(
                    ft.Text(f"❌ 无法打开目录: {ex}", color="red", size=12)
                )
                log_view.update()
    
    return handler

# ========== 本地化页面事件处理器 ==========

def create_localizer_handler(localizer_page):
    """创建开始本地化按钮的事件处理器"""
    def handler(e):
        log_view = localizer_page.get_component("log_view")
        
        if log_view:
            log_view.controls.append(
                ft.Text("🚧 本地化功能开发中...", color="orange", size=14)
            )
            log_view.update()
    
    return handler

def create_localizer_open_handler(localizer_page):
    """创建打开目录按钮的事件处理器（本地化）"""
    def handler(e):
        log_view = localizer_page.get_component("log_view")
        
        if log_view:
            log_view.controls.append(
                ft.Text("📂 本地化输出目录功能待实现", color="grey", size=12)
            )
            log_view.update()
    
    return handler

# ========== 设置页面事件处理器 ==========

def create_settings_config_handler(settings_page):
    """创建配置路径输入框事件处理器"""
    def handler(e):
        # 可以在这里添加配置变更逻辑
        print(f"配置路径变更为: {e.control.value}")
    
    return handler

def create_settings_save_handler(settings_page: SettingsPage):
    """创建保存配置按钮事件处理器"""
    def handler(e):
        try:
            # 1. 从表单获取最新配置
            config_data = settings_page.get_config()
            
            # 2. 验证配置
            if not config_data:
                print("⚠️ 配置为空，无法保存")
                return
            
            # 3. 写回config.json
            config_path = Path("config.json")
            config_path.write_text(
                json.dumps(config_data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            # 4. 获取日志组件并显示成功消息
            save_btn = settings_page.get_component("save_btn")
            if save_btn:
                save_btn.text = "✅ 保存成功"
                save_btn.bgcolor = ft.colors.GREEN
                save_btn.update()
                
                # 3秒后恢复按钮文字
                def restore_button():
                    save_btn.text = "💾 保存配置"
                    save_btn.bgcolor = ft.colors.BLUE
                    save_btn.update()
                
                settings_page.page.run_task(lambda: (restore_button(), None)[1], delay=3)
            
            print(f"✅ 配置已保存到 {config_path.absolute()}")
            
        except Exception as ex:
            print(f"❌ 保存配置失败: {ex}")
            save_btn = settings_page.get_component("save_btn")
            if save_btn:
                save_btn.text = "❌ 保存失败"
                save_btn.bgcolor = ft.colors.RED
                save_btn.update()
    
    return handler

def create_settings_dir_change_handler(settings_page: SettingsPage):
    """创建目录变更事件处理器（实时验证）"""
    def handler(e):
        field_name = e.control.label
        value = e.control.value
        
        # 验证目录是否存在
        dir_path = Path(value)
        if not dir_path.exists():
            print(f"⚠️ {field_name} 目录不存在: {value}")
        else:
            print(f"✅ {field_name} 已更新: {value}")
    
    return handler

# ========== 主入口 ==========

def main(page: ft.Page):
    """主入口"""
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    page.window_min_width = 600
    page.window_min_height = 500
    
    # 创建路由
    router = BaseRouter(page)
    
    # 创建页面实例
    home_page = HomePage(router, page)
    generator_page = GeneratorPage(router, page)
    localizer_page = LocalizerPage(router, page)
    settings_page = SettingsPage(router, page)
    
    # 注册页面
    router.add_route("home", "首页", ft.icons.HOME, home_page.build)
    router.add_route("generator", "生成器", ft.icons.BUILD, generator_page.build)
    router.add_route("localizer", "本地化", ft.icons.LANGUAGE, localizer_page.build)
    router.add_route("settings", "设置", ft.icons.SETTINGS, settings_page.build)
    
    # ========== 绑定事件（关键步骤） ==========
    
    # 首页事件
    home_page.register_go_generator_event(create_go_generator_handler(router))
    home_page.register_go_localizer_event(create_go_localizer_handler(router))
    
    # 生成器页面事件
    generator_page.register_dry_run_change_event(create_dry_run_handler(generator_page))
    generator_page.register_explain_change_event(create_explain_handler(generator_page))
    generator_page.register_generate_event(create_generator_handler(generator_page))
    generator_page.register_open_event(create_generator_open_handler(generator_page))
    
    # 本地化页面事件
    localizer_page.register_localize_event(create_localizer_handler(localizer_page))
    localizer_page.register_open_event(create_localizer_open_handler(localizer_page))
    
    # 设置页面事件
    settings_page.register_save_event(create_settings_save_handler(settings_page))
    settings_page.register_output_dir_change(
        create_settings_dir_change_handler(settings_page)
    )
    settings_page.register_template_dir_change(
        create_settings_dir_change_handler(settings_page)
    )

    # 绑定所有设置事件
    settings_page.bind_events()
    
    # 绑定所有事件到组件
    home_page.bind_events()
    generator_page.bind_events()
    localizer_page.bind_events()
    settings_page.bind_events()
    
    # 显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)