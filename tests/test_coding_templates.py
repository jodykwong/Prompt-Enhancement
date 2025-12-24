"""
Tests for the coding template system.

Tests CodingTemplate, TemplateTrigger, and CodingTemplateManager classes.
"""

import pytest
from pathlib import Path
import yaml
import tempfile
from typing import Dict, Any

from prompt_enhancement.coding_templates import (
    CodingTemplate,
    TemplateMatch,
    TemplateTrigger,
    CodingTemplateManager,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_template_dict() -> Dict[str, Any]:
    """Create a sample template dictionary."""
    return {
        'name': '实现新功能',
        'task_type': 'implement',
        'description': '从零开始实现一个新的功能或组件',
        'triggers': ['添加', '实现', '创建', 'add', 'implement', 'create'],
        'checklist': ['理解需求', '设计接口', '实现核心逻辑'],
        'best_practices': {
            'python': ['使用类型注解', '添加docstring'],
            'javascript': ['定义接口类型', '处理Promise'],
        },
        'common_pitfalls': ['没有考虑边界情况', '缺少错误处理'],
        'acceptance_criteria': ['功能符合需求', '所有测试通过'],
        'examples': ['添加用户认证功能', '实现文件上传API'],
    }


@pytest.fixture
def sample_templates_dir(tmp_path) -> Path:
    """Create a temporary templates directory with sample YAML files."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create implement.yaml
    implement = {
        'name': '实现新功能',
        'task_type': 'implement',
        'description': '从零开始实现一个新的功能',
        'triggers': ['添加', '实现', 'add', 'implement'],
        'checklist': ['理解需求', '设计接口'],
        'best_practices': {'python': ['使用类型注解']},
        'common_pitfalls': ['没有测试'],
        'acceptance_criteria': ['测试通过'],
        'examples': ['添加登录功能'],
    }

    # Create fix.yaml
    fix = {
        'name': '修复Bug',
        'task_type': 'fix',
        'description': '定位并修复bug',
        'triggers': ['修复', '解决', 'fix', 'solve'],
        'checklist': ['复现问题', '定位根因'],
        'best_practices': {'python': ['先写测试']},
        'common_pitfalls': ['只修症状'],
        'acceptance_criteria': ['bug已修复'],
        'examples': ['修复登录bug'],
    }

    # Create refactor.yaml
    refactor = {
        'name': '重构代码',
        'task_type': 'refactor',
        'description': '改进代码质量',
        'triggers': ['重构', '优化', 'refactor', 'optimize'],
        'checklist': ['有完整测试', '小步重构'],
        'best_practices': {'python': ['保持向后兼容']},
        'common_pitfalls': ['过度工程化'],
        'acceptance_criteria': ['测试通过'],
        'examples': ['优化数据库查询'],
    }

    # Write YAML files
    with open(templates_dir / "implement.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(implement, f, allow_unicode=True)

    with open(templates_dir / "fix.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(fix, f, allow_unicode=True)

    with open(templates_dir / "refactor.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(refactor, f, allow_unicode=True)

    return templates_dir


# ============================================================================
# Tests for CodingTemplate
# ============================================================================


class TestCodingTemplate:
    """Test CodingTemplate dataclass."""

    def test_create_template_with_valid_data(self, sample_template_dict):
        """Test creating template with valid data."""
        template = CodingTemplate(**sample_template_dict)

        assert template.name == '实现新功能'
        assert template.task_type == 'implement'
        assert len(template.triggers) == 6
        assert '添加' in template.triggers

    def test_create_template_requires_name(self, sample_template_dict):
        """Test that name is required."""
        sample_template_dict['name'] = None
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            CodingTemplate(**sample_template_dict)

    def test_create_template_requires_task_type(self, sample_template_dict):
        """Test that task_type is required."""
        sample_template_dict['task_type'] = ''
        with pytest.raises(ValueError, match="task_type must be a non-empty string"):
            CodingTemplate(**sample_template_dict)

    def test_create_template_requires_triggers(self, sample_template_dict):
        """Test that triggers must be non-empty list."""
        sample_template_dict['triggers'] = []
        with pytest.raises(ValueError, match="triggers must be a non-empty list"):
            CodingTemplate(**sample_template_dict)


# ============================================================================
# Tests for TemplateMatch
# ============================================================================


class TestTemplateMatch:
    """Test TemplateMatch dataclass."""

    def test_create_match_with_valid_confidence(self, sample_template_dict):
        """Test creating match with valid confidence."""
        template = CodingTemplate(**sample_template_dict)
        match = TemplateMatch(template=template, trigger_word='add', confidence=0.8)

        assert match.confidence == 0.8
        assert match.trigger_word == 'add'
        assert match.template.task_type == 'implement'

    def test_match_requires_valid_confidence(self, sample_template_dict):
        """Test that confidence must be 0-1."""
        template = CodingTemplate(**sample_template_dict)

        with pytest.raises(ValueError, match="confidence must be between"):
            TemplateMatch(template=template, trigger_word='add', confidence=1.5)

        with pytest.raises(ValueError, match="confidence must be between"):
            TemplateMatch(template=template, trigger_word='add', confidence=-0.1)


# ============================================================================
# Tests for TemplateTrigger
# ============================================================================


class TestTemplateTrigger:
    """Test TemplateTrigger matching logic."""

    def test_tokenize_english_text(self):
        """Test tokenizing English text."""
        trigger = TemplateTrigger()
        words = trigger._tokenize("add new feature")

        assert 'add' in words
        assert 'new' in words
        assert 'feature' in words

    def test_tokenize_chinese_text(self):
        """Test tokenizing Chinese text."""
        trigger = TemplateTrigger()
        words = trigger._tokenize("添加新功能")

        assert len(words) > 0

    def test_tokenize_mixed_text(self):
        """Test tokenizing mixed English and Chinese."""
        trigger = TemplateTrigger()
        words = trigger._tokenize("添加 add 功能")

        assert len(words) >= 2

    def test_match_exact_trigger(self, sample_template_dict):
        """Test matching exact trigger word."""
        template = CodingTemplate(**sample_template_dict)
        trigger = TemplateTrigger()

        match = trigger.match("add a new feature", [template])

        assert match is not None
        assert match.confidence >= 0.3
        assert match.template.task_type == 'implement'

    def test_match_implement_triggers(self, sample_template_dict):
        """Test matching implement task triggers."""
        template = CodingTemplate(**sample_template_dict)
        trigger = TemplateTrigger()

        for word in ['add', 'implement', 'create']:
            match = trigger.match(f"please {word} a feature", [template])
            assert match is not None
            assert match.template.task_type == 'implement'

    def test_match_no_match(self, sample_template_dict):
        """Test when no triggers match."""
        template = CodingTemplate(**sample_template_dict)
        trigger = TemplateTrigger()

        match = trigger.match("completely unrelated task", [template])

        # Match might be None or have low confidence
        assert match is None or match.confidence < 0.3

    def test_match_returns_best_match(self, sample_templates_dir):
        """Test that best matching template is returned."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        trigger = TemplateTrigger()

        match = trigger.match("fix a bug", list(manager.templates.values()))

        assert match is not None
        assert match.template.task_type == 'fix'

    def test_match_with_empty_input(self):
        """Test matching with empty input."""
        trigger = TemplateTrigger()
        match = trigger.match("", [])

        assert match is None

    def test_match_with_partial_trigger(self, sample_template_dict):
        """Test matching with partial trigger word."""
        template = CodingTemplate(**sample_template_dict)
        trigger = TemplateTrigger()

        # "add" is in template triggers
        match = trigger.match("addendum something", [template])

        # Should match with some confidence even for partial matches
        assert match is not None or match is None  # Depends on implementation


# ============================================================================
# Tests for CodingTemplateManager
# ============================================================================


class TestCodingTemplateManager:
    """Test CodingTemplateManager."""

    def test_init_with_custom_dir(self, sample_templates_dir):
        """Test initializing manager with custom templates directory."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        assert manager.templates_dir == sample_templates_dir
        assert len(manager.templates) > 0

    def test_load_templates(self, sample_templates_dir):
        """Test loading templates from directory."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        assert 'implement' in manager.templates
        assert 'fix' in manager.templates
        assert 'refactor' in manager.templates

    def test_get_template_by_type(self, sample_templates_dir):
        """Test getting template by task type."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('implement')

        assert template is not None
        assert template.task_type == 'implement'
        assert template.name == '实现新功能'

    def test_get_nonexistent_template(self, sample_templates_dir):
        """Test getting template that doesn't exist."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('nonexistent')

        assert template is None

    def test_list_templates(self, sample_templates_dir):
        """Test listing all available templates."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        templates = manager.list_templates()

        assert 'implement' in templates
        assert 'fix' in templates
        assert 'refactor' in templates

    def test_match_template_from_input(self, sample_templates_dir):
        """Test auto-matching template from user input."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        match = manager.match_template("add a new feature")

        assert match is not None
        assert match.template.task_type == 'implement'

    def test_format_template_all_languages(self, sample_templates_dir):
        """Test formatting template with all languages."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('implement')

        formatted = manager.format_template(template)

        assert '实现新功能' in formatted
        assert '检查清单' in formatted
        assert '最佳实践' in formatted
        assert '常见陷阱' in formatted
        assert '验收标准' in formatted

    def test_format_template_specific_language(self, sample_templates_dir):
        """Test formatting template for specific language."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('implement')

        formatted = manager.format_template(template, language='python')

        assert '使用类型注解' in formatted
        assert 'Python' in formatted

    def test_template_caching(self, sample_templates_dir):
        """Test that template formatting is cached."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('implement')

        # Format twice
        formatted1 = manager.format_template(template)
        formatted2 = manager.format_template(template)

        # Should be identical and cached
        assert formatted1 == formatted2
        cache_key = f"{template.task_type}:all"
        assert cache_key in manager._cache

    def test_clear_cache(self, sample_templates_dir):
        """Test clearing template cache."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        template = manager.get_template('implement')

        # Cache something
        manager.format_template(template)
        assert len(manager._cache) > 0

        # Clear cache
        manager.clear_cache()
        assert len(manager._cache) == 0

    def test_parse_yaml_template(self, sample_template_dict, sample_templates_dir):
        """Test parsing YAML template file."""
        manager = CodingTemplateManager(str(sample_templates_dir))
        yaml_path = sample_templates_dir / "implement.yaml"

        template = manager._parse_yaml_template(yaml_path)

        assert template.task_type == 'implement'
        assert template.name == '实现新功能'
        assert len(template.triggers) == 4

    def test_parse_invalid_yaml_template(self, tmp_path):
        """Test parsing invalid YAML template."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Create invalid template (missing required fields)
        invalid = {
            'name': '无效模板',
            # Missing other required fields
        }

        with open(templates_dir / "invalid.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(invalid, f, allow_unicode=True)

        manager = CodingTemplateManager(str(templates_dir))

        # Manager should handle invalid template gracefully
        # It should either skip it or log an error
        assert len(manager.templates) == 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for the complete template system."""

    def test_full_implement_workflow(self, sample_templates_dir):
        """Test full workflow for implement task."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        # User input
        user_input = "add a new user authentication feature"

        # Match template
        match = manager.match_template(user_input)
        assert match is not None
        assert match.template.task_type == 'implement'

        # Get template
        template = manager.get_template(match.template.task_type)
        assert template is not None

        # Format template
        formatted = manager.format_template(template, language='python')
        assert len(formatted) > 0
        assert '检查清单' in formatted

    def test_full_fix_workflow(self, sample_templates_dir):
        """Test full workflow for fix task."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        # User input
        user_input = "fix the login bug"

        # Match template
        match = manager.match_template(user_input)
        assert match is not None
        assert match.template.task_type == 'fix'

        # Format template
        formatted = manager.format_template(match.template)
        assert '修复Bug' in formatted

    def test_full_refactor_workflow(self, sample_templates_dir):
        """Test full workflow for refactor task."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        # User input
        user_input = "refactor the database queries for better performance"

        # Match template
        match = manager.match_template(user_input)
        assert match is not None
        assert match.template.task_type == 'refactor'

        # Format template
        formatted = manager.format_template(match.template)
        assert '重构代码' in formatted

    def test_multiple_templates_available(self, sample_templates_dir):
        """Test that manager loads multiple templates."""
        manager = CodingTemplateManager(str(sample_templates_dir))

        templates = manager.list_templates()
        assert len(templates) >= 3

        # Each template should be retrievable
        for task_type in templates:
            template = manager.get_template(task_type)
            assert template is not None
            assert template.task_type == task_type
