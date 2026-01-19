
import itertools
from typing import Dict, List, Tuple, Optional

class ReplacementEngine:
    """
    核心替换引擎（无状态，纯函数式）
    依赖：仅依赖 model.ReplacementRule
    """
    
    def __init__(self, default_namespace: str, rules: List):
        self.default_ns = default_namespace
        self.rules = {r.type: r for r in rules}  # 建立索引

    def generate_combinations(self, template) -> List[Dict]:
        """根据模板占位符生成笛卡尔积组合"""
        needed = set(template.placeholders)
        active_rules = [self.rules[t] for t in needed if t in self.rules]
        
        if not active_rules:
            return []
        
        value_lists = [r.values for r in active_rules]
        type_names = [r.type for r in active_rules]
        
        return [
            dict(zip(type_names, combo))
            for combo in itertools.product(*value_lists)
        ]

    def apply(self, content: str, combo: Dict, explain_log: Optional[List] = None) -> str:
        """执行所有替换逻辑"""
        # 1. 解析命名空间
        type_info = self._parse_combo(combo)
        
        # 2. 基础替换
        result = self._apply_basic(content, combo, type_info, explain_log)
        
        # 3. 额外规则替换
        result = self._apply_extra(result, combo, type_info, explain_log)
        
        return result

    def _parse_combo(self, combo: Dict) -> Dict[str, Tuple]:
        """解析组合中所有值的命名空间"""
        return {
            r_type: self._resolve(value)
            for r_type, value in combo.items()
        }

    def _resolve(self, value: str) -> Tuple[str, str, str]:
        """解析单个值的命名空间"""
        if ":" in value:
            ns, name = value.split(":", 1)
            return name, f"{ns}:", f"{ns}_"
        else:
            return value, self.default_ns, "" if self.default_ns == "minecraft:" else self.default_ns.replace(":", "_")

    def _apply_basic(self, content: str, combo: Dict, info: Dict, log: Optional[List]) -> str:
        """基础占位符替换 ({modid}, {tree}, 等)"""
        result = content
        
        # 系统占位符
        first_type = next(iter(combo), None)
        modid = info[first_type][1] if first_type else self.default_ns
        result = result.replace("{modid}", modid)
        result = result.replace("{modid_safe}", "" if modid == "minecraft:" else modid.replace(":", "_"))
        
        # 类型占位符
        for r_type, (name, _, _) in info.items():
            placeholder = f"{{{r_type}}}"
            if placeholder in result and log is not None:
                log.append(f"  → 替换 {placeholder} => {name}")
            result = result.replace(placeholder, name)
        
        return result

    def _apply_extra(self, content: str, combo: Dict, info: Dict, log: Optional[List]) -> str:
        """应用额外替换规则（优先级：完整值 > 纯名称 > 通配符）"""
        result = content
        
        for r_type, rule in self.rules.items():
            if r_type not in combo:
                continue
            
            name, namespace, _ = info[r_type]
            full_value = f"{namespace}{name}"
            extra = rule.extra
            
            # 优先级1：通配符（最低）
            if "*" in extra:
                for old, new in extra["*"].items():
                    if old in result:
                        if log: log.append(f"  → 通配符 [*]: {old} => {new}")
                        result = result.replace(old, new)
            
            # 优先级2：纯名称匹配
            if name in extra:
                for old, new in extra[name].items():
                    if old in result:
                        if log: log.append(f"  → 纯名称 [{name}]: {old} => {new}")
                        result = result.replace(old, new)
            
            # 优先级3：完整值匹配（最高）
            if full_value in extra:
                for old, new in extra[full_value].items():
                    if old in result:
                        if log: log.append(f"  → 完整值 [{full_value}]: {old} => {new}")
                        result = result.replace(old, new)
        
        return result