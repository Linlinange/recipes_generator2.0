
import flet as ft
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional

class BasePage(ABC):
    """
    页面基类：只负责UI展示和事件注册
    事件处理逻辑由外部注入
    """
    
    def __init__(self, router: Any, page: ft.Page):
        self.router = router
        self.page = page
        self.components: Dict[str, ft.Control] = {}
        self._event_handlers: Dict[str, Dict[str, Callable]] = {}
    
    def add_component(self, name: str, component: ft.Control) -> ft.Control:
        """注册组件，方便后续访问"""
        self.components[name] = component
        return component
    
    def get_component(self, name: str) -> Optional[ft.Control]:
        """获取已注册的组件"""
        return self.components.get(name)

    def register_event(self, component_name: str, event_type: str, handler: Callable):
        """注册组件事件"""
        component = self.get_component(component_name)
        if not component:
            raise ValueError(f"❌ 致命错误：组件 '{component_name}' 不存在！可用组件: {list(self.components.keys())}")
        
        # 存储处理器
        self._event_handlers[f"{component_name}_{event_type}"] = {
            "component": component,
            "handler": handler,
        }

    def bind_events(self):
        """绑定所有事件（带调试）"""
        print(f"📌 绑定页面事件，共 {len(self._event_handlers)} 个")
        for event_key, event_data in self._event_handlers.items():
            component = event_data["component"]
            handler = event_data["handler"]
            print(f"  → 绑定 {event_key}")
            
            # 安全绑定
            try:
                if event_key.endswith("_click"):
                    component.on_click = handler
                elif event_key.endswith("_change"):
                    component.on_change = handler
                elif event_key.endswith("_submit"):
                    component.on_submit = handler
            except Exception as e:
                raise RuntimeError(f"绑定 {event_key} 失败: {e}")
    
    @abstractmethod
    def build(self) -> ft.Control:
        """子类必须实现：返回页面UI结构"""
        pass