
from pathlib import Path
import sys
import os
import json

# 将src加入Python路径
sys.path.append(str(Path(__file__).parent))

def test_model_layer():
    """测试Model层"""
    print("=" * 60)
    print("🧪 测试 Model 层")
    print("=" * 60)
    
    try:
        from src.model.template import Template
        from src.model.config import Config, ReplacementRule
        
        # 1. 测试 Template
        print("\n[测试 Template 类]")
        
        # 创建临时测试模板
        test_content = '{"item": "{tree}_{tool}", "namespace": "{modid}"}'
        test_file = Path("test_temp_template.json")
        test_file.write_text(test_content, encoding='utf-8')
        
        template = Template(test_file)
        print(f"✅ 模板路径: {template.path.name}")
        print(f"✅ 识别到的占位符: {template.placeholders}")
        assert 'tree' in template.placeholders, "应该识别到 tree 占位符"
        assert 'tool' in template.placeholders, "应该识别到 tool 占位符"
        
        test_file.unlink()  # 清理临时文件
        
        # 2. 测试 Config
        print("\n[测试 Config 类]")
        config_data = {
            "output_dir": "./test_output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": ["test.json"],
            "replacements": [
                {"type": "tree", "values": ["oak", "pine"], "extra": {}},
                {"type": "tool", "values": ["axe", "sword"], "extra": {}}
            ]
        }
        
        config = Config(config_data)
        print(f"✅ 输出目录: {config.output_dir}")
        print(f"✅ 默认命名空间: {config.default_namespace}")
        print(f"✅ 模板文件列表: {config.template_files}")
        print(f"✅ 替换规则数: {len(config.rules)}")
        
        rule = config.rules[0]
        print(f"✅ 第一条规则类型: {rule.type}, 值数量: {len(rule.values)}")
        
        assert len(config.rules) == 2, "应该有2条规则"
        assert config.rules[0].type == "tree", "第一条规则类型应该是 tree"
        
        print("\n✅ Model 层测试全部通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Model 层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_core_layer():
    """测试Core层"""
    print("\n" + "=" * 60)
    print("🧪 测试 Core 层")
    print("=" * 60)
    
    try:
        from src.model.config import ReplacementRule
        from src.core.engine import ReplacementEngine
        
        # 准备数据
        rules = [
            ReplacementRule(
                type='tree', 
                values=['oak', 'bamboo'],
                extra={
                    '*': {'LOG': 'WOOD'},  # 通配符规则
                    'bamboo': {'SPECIAL': 'BAMBOO_BLOCK'}  # 具体规则
                }
            ),
            ReplacementRule(type='tool', values=['axe'], extra={})
        ]
        
        # 1. 测试组合生成
        print("\n[测试组合生成]")
        engine = ReplacementEngine('minecraft:', rules)
        
        # 模拟模板对象
        class MockTemplate:
            placeholders = ['tree', 'tool']
        
        combos = engine.generate_combinations(MockTemplate())
        print(f"✅ 生成组合数量: {len(combos)}")
        for i, combo in enumerate(combos[:3]):  # 显示前3个
            print(f"   组合 {i+1}: {combo}")
        
        assert len(combos) == 2, "应该生成2个组合（2树种 × 1工具）"
        
        # 2. 测试基础替换
        print("\n[测试基础替换]")
        content = "{modid}{tree}_{tool}"
        result = engine.apply(content, combos[0])
        print(f"✅ 输入: {content}")
        print(f"✅ 输出: {result}")
        assert "minecraft:oak_axe" in result, "应该正确替换占位符"
        
        # 3. 测试额外规则（通配符）
        print("\n[测试额外规则 - 通配符]")
        content_with_extra = "{tree}_{tool} uses LOG"
        result = engine.apply(content_with_extra, combos[0], explain_log=[])
        print(f"✅ 输入: {content_with_extra}")
        print(f"✅ 输出: {result}")
        assert "WOOD" in result, "通配符规则应该生效"
        
        # 4. 测试额外规则（具体值）
        print("\n[测试额外规则 - 具体值]")
        # 使用包含 SPECIAL 的模板来测试 bamboo 特定规则
        content_with_special = "{tree}_{tool} uses SPECIAL"
        result = engine.apply(content_with_special, combos[1], explain_log=[])
        print(f"✅ bamboo 组合输出: {result}")
        assert "BAMBOO_BLOCK" in result, "bamboo的特定规则应该生效"
        
        # 验证 oak 不使用 bamboo 规则
        result_oak = engine.apply(content_with_special, combos[0], explain_log=[])
        print(f"✅ oak 组合输出: {result_oak}")
        assert result_oak == "oak_axe uses SPECIAL", "oak 不应该触发 bamboo 规则"
        
        print("\n✅ Core 层测试全部通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Core 层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dao_layer():
    """测试DAO层（Loader + Writer）"""
    print("\n" + "=" * 60)
    print("🧪 测试 DAO 层")
    print("=" * 60)
    
    try:
        from src.dao.config_dao import ConfigDAO
        from src.dao.template_loader import TemplateLoader
        from src.dao.output_writer import OutputWriter
        
        # 1. 测试 ConfigDAO
        print("\n[测试 ConfigDAO]")
        
        config_data = {
            "output_dir": "./test_output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "replacements": [
                {"type": "tree", "values": ["oak", "birch"], "extra": {}}
            ]
        }
        
        temp_config = Path("test_temp_config.json")
        temp_config.write_text(json.dumps(config_data), encoding='utf-8')
        
        config = ConfigDAO.load("test_temp_config.json")
        print(f"✅ 配置加载成功")
        print(f"   输出目录: {config.output_dir}")
        print(f"   规则数量: {len(config.rules)}")
        assert len(config.rules) == 1
        
        temp_config.unlink()
        
        # 2. 测试 TemplateLoader
        print("\n[测试 TemplateLoader]")
        
        temp_template = Path("templates/test_loader.json")
        temp_template.parent.mkdir(exist_ok=True)
        temp_template.write_text('{"item": "{tree}_planks"}', encoding='utf-8')
        
        loader = TemplateLoader(Path("templates"))
        templates = loader.load_all(["test_loader.json"])
        print(f"✅ 加载模板: {len(templates)} 个")
        assert "test_loader.json" in templates
        
        # 3. 测试 OutputWriter
        print("\n[测试 OutputWriter]")
        
        output_dir = Path("test_writer_output")
        writer = OutputWriter(output_dir)
        
        test_content = '{"item": "oak_planks"}'
        output_path = writer.write("test_output.json", test_content, dry_run=False)
        print(f"✅ 写入文件: {output_path.name}")
        assert output_path.exists()
        
        # 验证内容
        written_data = json.loads(output_path.read_text(encoding='utf-8'))
        assert written_data["item"] == "oak_planks"
        
        # 验证统计
        stats = writer.get_stats()
        print(f"✅ 统计: {stats}")
        assert stats["total"] == 1
        
        # 清理
        temp_template.unlink()
        output_path.unlink()
        output_dir.rmdir()
        
        print("\n✅ DAO 层测试全部通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ DAO 层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n🎯 开始分层测试...")
    
    results = []
    results.append(test_model_layer())
    results.append(test_core_layer())
    results.append(test_dao_layer())  # 添加这一行
    
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"Model 层: {'✅ 通过' if results[0] else '❌ 失败'}")
    print(f"Core 层:  {'✅ 通过' if results[1] else '❌ 失败'}")
    print(f"DAO 层:  {'✅ 通过' if results[2] else '❌ 失败'}")
    
    if all(results):
        print("\n🎉 所有测试通过！可以继续下一层重构了。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查代码。")
        sys.exit(1)

if __name__ == "__main__":
    main()