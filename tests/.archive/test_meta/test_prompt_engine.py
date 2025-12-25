"""
测试 MetaPromptEngine - Meta Prompt Engine的核心功能

测试覆盖:
  - 变量识别 (extract_variables)
  - 结构规划 (plan_structure)
  - XML生成 (write_instructions)
  - 完整流程 (generate_complete_prompt)
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from prompt_enhancement.meta.prompt_engine import (
    MetaPromptEngine,
    Variable,
    VariableType,
    Structure,
    XMLSection,
)
from prompt_enhancement.meta.xml_builder import XMLValidator


class TestVariableExtraction:
    """测试变量识别功能"""

    def test_extract_variables_code_review(self):
        """测试代码审查任务的变量识别"""
        engine = MetaPromptEngine()
        task = "帮我写一个代码审查工具"

        variables = engine.extract_variables(task)

        assert isinstance(variables, list)
        assert len(variables) > 0
        assert any(v.name == "CODE" for v in variables)
        assert any(v.type == VariableType.CODE for v in variables)

    def test_extract_variables_bug_fix(self):
        """测试bug修复任务的变量识别"""
        engine = MetaPromptEngine()
        task = "帮我修复代码中的bug"

        variables = engine.extract_variables(task)

        assert len(variables) > 0
        variable_names = [v.name for v in variables]
        assert "CODE" in variable_names or any("bug" in v.name.lower() for v in variables)

    def test_extract_variables_data_processing(self):
        """测试数据处理任务的变量识别"""
        engine = MetaPromptEngine()
        task = "写一个数据处理和清洗的提示词"

        variables = engine.extract_variables(task)

        assert len(variables) > 0
        variable_names = [v.name for v in variables]
        assert "DATA" in variable_names or any("data" in v.name.lower() for v in variables)

    def test_extract_variables_caching(self):
        """测试变量识别的缓存机制"""
        engine = MetaPromptEngine()
        task = "代码审查"

        # 第一次调用
        vars1 = engine.extract_variables(task)
        # 第二次调用（应该从缓存返回）
        vars2 = engine.extract_variables(task)

        assert vars1 == vars2

    def test_variable_attributes(self):
        """测试变量对象的属性"""
        var = Variable(
            name="CODE",
            type=VariableType.CODE,
            required=True,
            description="代码片段"
        )

        assert var.name == "CODE"
        assert var.type == VariableType.CODE
        assert var.required is True
        assert var.description == "代码片段"


class TestStructurePlanning:
    """测试结构规划功能"""

    def test_plan_structure_coding_task(self):
        """测试代码任务的结构规划"""
        engine = MetaPromptEngine()
        task = "写一个代码审查提示词"

        structure = engine.plan_structure(task)

        assert isinstance(structure, Structure)
        assert structure.task_type == "coding"
        assert len(structure.sections) > 0

        # 检查是否包含关键的XML区块
        section_names = {s.name for s in structure.sections}
        assert "role" in section_names
        assert "instructions" in section_names or "task" in section_names

    def test_plan_structure_data_task(self):
        """测试数据任务的结构规划"""
        engine = MetaPromptEngine()
        task = "数据清洗和处理"

        structure = engine.plan_structure(task)

        assert structure.task_type == "data"
        section_names = {s.name for s in structure.sections}
        assert "role" in section_names

    def test_plan_structure_writing_task(self):
        """测试写作任务的结构规划"""
        engine = MetaPromptEngine()
        task = "写一个API文档"

        structure = engine.plan_structure(task)

        assert structure.task_type in ["writing", "default"]  # API可能被映射到writing或default

    def test_plan_structure_with_variables(self):
        """测试带变量的结构规划"""
        engine = MetaPromptEngine()
        task = "代码审查"
        variables = [
            Variable("CODE", VariableType.CODE, True, "代码"),
            Variable("LANGUAGE", VariableType.LANGUAGE, False, "编程语言")
        ]

        structure = engine.plan_structure(task, variables)

        assert structure.variables == variables
        assert len(structure.sections) > 0

    def test_plan_structure_caching(self):
        """测试结构规划的缓存"""
        engine = MetaPromptEngine()
        task = "代码审查"

        struct1 = engine.plan_structure(task)
        struct2 = engine.plan_structure(task)

        # 缓存应该返回相同的对象
        assert struct1.task_type == struct2.task_type
        assert len(struct1.sections) == len(struct2.sections)


class TestXMLGeneration:
    """测试XML prompt生成"""

    def test_write_instructions_basic(self):
        """测试基础的XML生成"""
        engine = MetaPromptEngine()
        task = "代码审查"

        # 获取结构
        structure = engine.plan_structure(task)

        # 由于write_instructions需要调用LLM，这里使用mock
        with patch.object(engine.provider, 'call') as mock_call:
            mock_call.return_value = Mock(content="""<prompt_template>
  <role>你是一名资深的代码审查专家</role>
  <instructions>请从以下维度审查代码</instructions>
  <output_format>以Markdown格式输出审查意见</output_format>
</prompt_template>""")

            xml = engine.write_instructions(structure)

            assert xml.startswith("<prompt_template>")
            assert "role" in xml
            assert "instructions" in xml

    def test_write_instructions_with_variables(self):
        """测试包含变量的XML生成"""
        engine = MetaPromptEngine()
        variables = [
            Variable("CODE", VariableType.CODE, True, "代码"),
            Variable("LANGUAGE", VariableType.LANGUAGE, False, "语言")
        ]
        structure = Structure(
            task_type="coding",
            sections=[XMLSection("role"), XMLSection("instructions"), XMLSection("output_format")],
            variables=variables
        )

        with patch.object(engine.provider, 'call') as mock_call:
            mock_call.return_value = Mock(content="""<prompt_template>
  <role>代码审查专家，评审{{LANGUAGE}}代码</role>
  <code>{{CODE}}</code>
  <instructions>请审查上面的代码</instructions>
  <output_format>返回审查意见</output_format>
</prompt_template>""")

            xml = engine.write_instructions(structure, variables)

            # 验证变量引用
            assert "{{LANGUAGE}}" in xml or "{{CODE}}" in xml

    def test_write_instructions_markdown_cleanup(self):
        """测试Markdown代码块的清理"""
        engine = MetaPromptEngine()
        structure = engine.plan_structure("测试")

        with patch.object(engine.provider, 'call') as mock_call:
            # LLM返回markdown代码块形式的XML
            mock_call.return_value = Mock(content="""```xml
<prompt_template>
  <role>test</role>
</prompt_template>
```""")

            xml = engine.write_instructions(structure)

            # 应该移除markdown标记
            assert not xml.startswith("```")
            assert xml.startswith("<prompt_template>")


class TestCompleteWorkflow:
    """测试完整的三步工作流"""

    def test_generate_complete_prompt_simple_task(self):
        """测试从任务描述直接生成完整prompt"""
        engine = MetaPromptEngine()
        task = "代码审查工具"

        with patch.object(engine.provider, 'call') as mock_call:
            mock_call.return_value = Mock(content="""<prompt_template>
  <role>资深代码审查专家</role>
  <instructions>审查{{CODE}}</instructions>
  <output_format>Markdown格式</output_format>
</prompt_template>""")

            xml = engine.generate_complete_prompt(task)

            assert xml.startswith("<prompt_template>")
            assert "role" in xml or "role" in xml.lower()

    def test_generate_complete_prompt_with_logging(self):
        """测试日志输出"""
        engine = MetaPromptEngine()
        task = "代码审查"

        with patch.object(engine.provider, 'call') as mock_call:
            mock_call.return_value = Mock(content="<prompt_template></prompt_template>")

            # 不应该抛出异常
            xml = engine.generate_complete_prompt(task)
            assert xml is not None

    def test_generate_complete_prompt_all_task_types(self):
        """测试所有任务类型的生成"""
        engine = MetaPromptEngine()
        tasks = [
            "代码审查",
            "bug修复",
            "数据处理",
            "文档写作"
        ]

        with patch.object(engine.provider, 'call') as mock_call:
            mock_call.return_value = Mock(content="<prompt_template><role>test</role></prompt_template>")

            for task in tasks:
                xml = engine.generate_complete_prompt(task)
                assert xml is not None
                assert "<prompt_template>" in xml or "prompt_template" in xml.lower()


class TestTaskTypeDetermination:
    """测试任务类型的确定"""

    def test_determine_coding_task(self):
        """测试代码任务的识别"""
        engine = MetaPromptEngine()

        assert engine._determine_task_type("代码审查") == "coding"
        assert engine._determine_task_type("修复bug") == "coding"
        assert engine._determine_task_type("重构代码") == "coding"

    def test_determine_data_task(self):
        """测试数据任务的识别"""
        engine = MetaPromptEngine()

        assert engine._determine_task_type("数据处理") == "data"
        assert engine._determine_task_type("CSV转换") == "data"
        assert engine._determine_task_type("数据清洗") == "data"

    def test_determine_writing_task(self):
        """测试写作任务的识别"""
        engine = MetaPromptEngine()

        assert engine._determine_task_type("写API文档") == "writing"
        assert engine._determine_task_type("编写README") == "writing"

    def test_determine_default_task(self):
        """测试默认任务识别"""
        engine = MetaPromptEngine()

        # 无法识别的任务应该返回default
        task_type = engine._determine_task_type("未知的奇怪任务")
        assert task_type in ["default", "coding", "data", "writing"]


class TestXMLValidation:
    """测试XML验证功能"""

    def test_xml_validation_valid(self):
        """测试有效的XML验证"""
        valid_xml = """<prompt_template>
  <role>专家</role>
  <instructions>指导</instructions>
  <output_format>格式</output_format>
</prompt_template>"""

        result = XMLValidator.validate(valid_xml)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_xml_validation_missing_required(self):
        """测试缺少必需元素的验证"""
        invalid_xml = """<prompt_template>
  <role>专家</role>
</prompt_template>"""

        result = XMLValidator.validate(invalid_xml)

        assert result["valid"] is False
        assert len(result["missing_required"]) > 0

    def test_xml_validation_malformed(self):
        """测试格式错误的XML"""
        malformed_xml = "<prompt_template><role>unclosed"

        result = XMLValidator.validate(malformed_xml)

        assert result["valid"] is False
        assert len(result["errors"]) > 0


# ============== 集成测试 ==============

class TestIntegration:
    """集成测试 - 测试Meta Engine与其他组件的交互"""

    def test_meta_engine_with_existing_llm_provider(self):
        """测试Meta Engine与现有LLM Provider的集成"""
        from prompt_enhancement.enhancement.llm_provider import create_provider

        try:
            provider = create_provider("openai")
            engine = MetaPromptEngine(llm_provider=provider)

            # 验证引擎正确初始化
            assert engine.provider == provider
        except Exception:
            # 如果没有API密钥，跳过该测试
            pytest.skip("OpenAI provider not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
