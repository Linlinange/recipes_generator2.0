
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
        """
        注册组件事件处理器
        但不实现具体逻辑，只是建立映射
        
        Args:
            component_name: 组件名称
            event_type: 事件类型（click, change等）
            handler: 回调函数
        """
        component = self.get_component(component_name)
        if not component:
            raise ValueError(f"组件 '{component_name}' 不存在")
        
        # 存储处理器
        self._event_handlers[f"{component_name}_{event_type}"] = {
            "component": component,
            "handler": handler,
        }
    
    def bind_events(self):
        """
        绑定所有注册的事件
        这个方法由run_flet.py调用
        """
        for event_key, event_data in self._event_handlers.items():
            component = event_data["component"]
            handler = event_data["handler"]
            
            # 根据事件类型设置
            if event_key.endswith("_click"):
                component.on_click = handler
            elif event_key.endswith("_change"):
                component.on_change = handler
            elif event_key.endswith("_submit"):
                component.on_submit = handler
    
    @abstractmethod
    def build(self) -> ft.Control:
        """子类必须实现：返回页面UI结构"""
        pass