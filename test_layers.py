
import json
from pathlib import Path
import sys
import os
import shutil

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
        assert 'tree' in template.placeholders
        assert 'tool' in template.placeholders
        
        test_file.unlink()
        
        # 2. 测试 Config 和 ReplacementRule
        print("\n[测试 Config 类]")
        config_data = {
            "output_dir": "./test_output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": ["test.json"],
            "replacements": [
                {"type": "tree", "values": ["oak", "pine"], "extra": {}}
            ]
        }
        
        config = Config(config_data)
        print(f"✅ 输出目录: {config.output_dir}")
        print(f"✅ 规则数量: {len(config.rules)}")
        
        rule = config.rules[0]
        print(f"✅ 第一条规则类型: {rule.type}, 值: {rule.values}")
        
        assert len(config.rules) == 1
        assert config.rules[0].type == "tree"
        
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
                    '*': {'LOG': 'WOOD'},
                    'bamboo': {'SPECIAL_MATERIAL': 'BAMBOO_BLOCK'}
                }
            ),
            ReplacementRule(type='tool', values=['axe'], extra={})
        ]
        
        # 1. 测试组合生成
        print("\n[测试组合生成]")
        engine = ReplacementEngine('minecraft:', rules)
        
        class MockTemplate:
            placeholders = ['tree', 'tool']
        
        combos = engine.generate_combinations(MockTemplate())
        print(f"✅ 生成组合数量: {len(combos)}")
        for i, combo in enumerate(combos[:3]):
            print(f"   组合 {i+1}: {combo}")
        
        assert len(combos) == 2
        
        # 2. 测试基础替换
        print("\n[测试基础替换]")
        content = "{modid}{tree}_{tool}"
        result = engine.apply(content, combos[0])
        print(f"✅ 输入: {content}")
        print(f"✅ 输出: {result}")
        assert "minecraft:oak_axe" in result
        
        # 3. 测试额外规则（通配符）
        print("\n[测试通配符规则]")
        content_with_extra = "{tree}_{tool} uses LOG"
        result = engine.apply(content_with_extra, combos[0], explain_log=[])
        print(f"✅ 输出: {result}")
        assert "WOOD" in result
        
        # 4. 测试额外规则（具体值）
        print("\n[测试特定规则]")
        content_with_special = "{tree}_{tool} uses SPECIAL_MATERIAL"
        result = engine.apply(content_with_special, combos[1], explain_log=[])
        print(f"✅ bamboo 输出: {result}")
        assert "BAMBOO_BLOCK" in result
        
        # 验证 oak 不触发 bamboo 规则
        result_oak = engine.apply(content_with_special, combos[0], explain_log=[])
        assert result_oak == "oak_axe uses SPECIAL_MATERIAL"
        
        print("\n✅ Core 层测试全部通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Core 层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dao_layer():
    """测试DAO层"""
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
            "output_dir": "./test_dao_output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "replacements": [{"type": "tree", "values": ["oak", "birch"], "extra": {}}]
        }
        
        temp_config = Path("test_temp_config.json")
        temp_config.write_text(json.dumps(config_data), encoding='utf-8')
        
        config = ConfigDAO.load("test_temp_config.json")
        print(f"✅ 配置加载成功")
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
        output_dir = Path("test_dao_output")
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

def test_service_layer():
    """测试Service层（完整流程）"""
    print("\n" + "=" * 60)
    print("🧪 测试 Service 层")
    print("=" * 60)
    
    try:
        from src.service.recipe_service import RecipeService
        
        # 1. 准备测试配置
        config_data = {
            "output_dir": "./test_service_output",
            "template_dir": "./test_templates",
            "default_namespace": "minecraft:",
            "template_files": ["{tree}_table.json"],
            "replacements": [
                {
                    "type": "tree", 
                    "values": ["oak", "birch"],
                    "extra": {
                        "*": {"_planks": "_wood"},  # 通配符规则
                        "minecraft:birch": {"__BIRCH_SPECIAL__": "birch_special_item"}  # 使用独特标记
                    }
                }
            ]
        }
        
        # 2. 创建临时配置
        Path("test_service_config.json").write_text(
            json.dumps(config_data), encoding='utf-8'
        )
        
        # 3. 创建模板
        template_dir = Path("test_templates")
        template_dir.mkdir(exist_ok=True)
        
        # ✅ 修复：模板文件名带占位符
        test_template = '''{
  "type": "minecraft:crafting_shaped",
  "pattern": ["##", "##"],
  "key": {"#": {"item": "minecraft:{tree}_planks"}},
  "result": {"item": "minecraft:{tree}__BIRCH_SPECIAL__", "count": 1}
}'''
        (template_dir / "{tree}_table.json").write_text(test_template, encoding='utf-8')
        
        # 4. 测试预览模式
        print("\n[测试预览模式]")
        service = RecipeService("test_service_config.json")
        service.run(dry_run=True, explain_mode=False)
        
        stats = service.output_writer.get_stats()
        print(f"✅ 预览模式统计: {stats}")
        assert stats["total"] == 2
        
        # 5. 测试实际写入
        service.output_writer.stats["total"] = 0  # 重置统计
        
        print("\n[测试实际写入]")
        service.run(dry_run=False, explain_mode=False)
        
        output_dir = Path("test_service_output")
        print(f"检查输出目录: {output_dir.absolute()}")
        print(f"目录存在: {output_dir.exists()}")
        if output_dir.exists():
            files = list(output_dir.glob("*.json"))
            print(f"目录内容: {files}")
        
        # ✅ 修复：预期文件名
        oak_file = output_dir / "oak_table.json"
        birch_file = output_dir / "birch_table.json"
        
        print(f"检查 oak 文件: {oak_file.absolute()}")
        print(f"oak 文件存在: {oak_file.exists()}")
        print(f"检查 birch 文件: {birch_file.absolute()}")
        print(f"birch 文件存在: {birch_file.exists()}")
        
        assert oak_file.exists(), f"文件不存在: {oak_file.absolute()}"
        assert birch_file.exists(), f"文件不存在: {birch_file.absolute()}"
        
        # 6. 验证内容
        print("\n[验证文件内容]")
        
        oak_data = json.loads(oak_file.read_text(encoding='utf-8'))
        print(f"✅ oak 文件内容: {oak_data}")
        # oak 应该只有通配符规则生效
        assert "oak_wood" in str(oak_data)
        assert "__BIRCH_SPECIAL__" in str(oak_data)  # 特殊标记保持不变
        
        birch_data = json.loads(birch_file.read_text(encoding='utf-8'))
        print(f"✅ birch 文件内容: {birch_data}")
        # birch 应该通配符和特定规则都生效
        assert "birch_wood" in str(birch_data)
        assert "birch_special_item" in str(birch_data)  # ✅ 修复这行
        assert "__BIRCH_SPECIAL__" not in str(birch_data)  # 标记被替换
        
        # 7. 验证统计
        stats = service.output_writer.get_stats()
        print(f"✅ 最终统计: {stats}")
        assert stats["total"] == 2
        
        # 8. 清理
        print("\n[清理测试文件]")
        Path("test_service_config.json").unlink()
        shutil.rmtree(template_dir)
        shutil.rmtree(output_dir)
        
        print("\n✅ Service 层测试全部通过！")
        return True
        
    except AssertionError as e:
        print(f"\n❌ 断言失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Service 层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n🎯 开始分层测试...")
    
    results = []
    results.append(test_model_layer())
    results.append(test_core_layer())
    results.append(test_dao_layer())
    results.append(test_service_layer())
    
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"Model 层:   {'✅ 通过' if results[0] else '❌ 失败'}")
    print(f"Core 层:    {'✅ 通过' if results[1] else '❌ 失败'}")
    print(f"DAO 层:     {'✅ 通过' if results[2] else '❌ 失败'}")
    print(f"Service 层: {'✅ 通过' if results[3] else '❌ 失败'}")
    
    if all(results):
        print("\n🎉 所有测试通过！重构成功！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查代码。")
        sys.exit(1)

if __name__ == "__main__":
    main()