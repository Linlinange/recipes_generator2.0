#!/usr/bin/env python3
"""
生命周期测试脚本
诊断问题：为什么组件创建失败？
"""

from pathlib import Path
import sys
import flet as ft

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_page import BasePage
from abc import ABC

# ==================== 测试1：BasePage是否调用build() ====================

print("=" * 70)
print("测试1：验证BasePage.__init__是否自动调用build()")
print("=" * 70)

# 创建Mock Page
class MockPage:
    def update(self): pass

# 创建测试用的HomePage
class TestHomePage(BasePage):
    def build(self) -> ft.Control:
        print("  → HomePage.build() 被调用")
        self.add_component("test_btn", ft.Button("测试按钮"))
        return ft.Column([self.get_component("test_btn")])

try:
    print("[步骤1] 实例化TestHomePage...")
    home = TestHomePage(None, MockPage())
    
    print(f"[步骤2] 实例化后组件: {list(home.components.keys())}")
    print(f"[步骤3] 组件数量: {len(home.components)}")
    
    if "test_btn" in home.components:
        print("✅ 测试1通过：build()在__init__中被调用")
    else:
        print("❌ 测试1失败：build()未被调用，组件为空")
        print("  问题原因：BasePage.__init__缺少self.build()")
        
except ValueError as e:
    print(f"❌ 测试1异常: {e}")
    print("  问题原因：register_event在组件创建前被调用")

print()

# ==================== 测试2：验证事件注册时序 ====================

print("=" * 70)
print("测试2：验证事件注册是否发生在build()之后")
print("=" * 70)

class TestPage2(BasePage):
    def build(self) -> ft.Control:
        self.add_component("btn", ft.Button("点击我"))
        return ft.Column([self.get_component("btn")])

try:
    print("[步骤1] 实例化...")
    page2 = TestPage2(None, MockPage())
    
    print(f"[步骤2] build()后组件: {list(page2.components.keys())}")
    
    print("[步骤3] 注册事件...")
    page2.register_event("btn", "click", lambda e: print("按钮被点击"))
    
    print("[步骤4] 绑定事件...")
    page2.bind_events()
    
    print("✅ 测试2通过：事件注册成功")
    
except Exception as e:
    print(f"❌ 测试2失败: {e}")

print()

# ==================== 测试3：验证Router的lambda包装 ====================

print("=" * 70)
print("测试3：验证Router.add_route的builder参数")
print("=" * 70)

class MockRouter:
    def __init__(self):
        self.routes = {}
    
    def add(self, name, builder):
        """模拟BaseRouter.add_route"""
        self.routes[name] = builder
    
    def call(self, name):
        """模拟router.go()时调用builder"""
        print(f"[Router] 调用路由 '{name}' 的builder...")
        content = self.routes[name]()
        print(f"[Router] builder返回: {type(content)}")

# 创建测试页面
test_page = TestPage2(None, MockPage())

# 方式A：直接传方法（错误方式）
print("\n--- 方式A：直接传方法引用 ---")
router_a = MockRouter()
router_a.add("bad", test_page.build)  # 没有lambda
try:
    router_a.call("bad")
except Exception as e:
    print(f"❌ 方式A失败: {e}")

# 方式B：用lambda包装（正确方式）
print("\n--- 方式B：用lambda包装 ---")
router_b = MockRouter()
router_b.add("good", lambda: test_page.build())  # ✅ 用lambda
try:
    router_b.call("good")
    print("✅ 方式B成功")
except Exception as e:
    print(f"❌ 方式B失败: {e}")

print()

# ==================== 测试4：完整整合测试 ====================

print("=" * 70)
print("测试4：模拟完整的项目流程")
print("=" * 70)

# 创建真实Router
from src.interfaces.base_router import BaseRouter

def test_full_flow():
    page = MockPage()
    router = BaseRouter(page)
    
    # 创建页面（使用lambda）
    home = TestPage2(None, page)
    
    print("[步骤1] 添加路由...")
    router.add_route("home", "首页", ft.icons.HOME, lambda: home.build())
    
    print("[步骤2] 注册事件...")
    home.register_event("btn", "click", lambda e: print("点击事件触发"))
    
    print("[步骤3] 绑定事件...")
    home.bind_events()
    
    print("[步骤4] 切换路由...")
    try:
        router.go("home")
        print("✅ 测试4通过：完整流程成功")
    except Exception as e:
        print(f"❌ 测试4失败: {e}")

test_full_flow()

print("=" * 70)
print("测试总结")
print("=" * 70)

print("如果测试1失败 → 问题在BasePage.__init__")
print("如果测试2失败 → 问题在事件注册时机")
print("如果测试3失败 → 问题在Router.add_route的参数")
print("如果测试4失败 → 问题在整合流程")