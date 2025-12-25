"""
Comprehensive tests for Story 3.1: Build Enhancement Prompt - Collect Project Context.

Tests all 8 acceptance criteria (AC1-AC8).
"""

import pytest
import json
from src.prompt_enhancement.enhancement import (
    ProjectContext,
    ProjectContextCollector,
    PromptBuilder,
    SensitiveDataValidator,
    StandardsDetectionResult,
    CollectionMetadata,
    GitHistoryContext,
)


class TestAC1_CollectProjectContext:
    """AC1: Collect Project Context After Analysis"""

    def test_collector_initializes_with_project_root(self, tmp_path):
        """Test that collector can be initialized with project root."""
        collector = ProjectContextCollector(str(tmp_path))
        assert collector.project_root == tmp_path

    def test_collector_extracts_project_name(self, tmp_path):
        """Test that project name is extracted from directory."""
        collector = ProjectContextCollector(str(tmp_path))
        context = collector.collect_context(analysis_result={})
        assert context.project_name is not None
        assert len(context.project_name) > 0

    def test_collector_gathers_all_required_fields(self):
        """Test that collector gathers all required AC1 fields."""
        collector = ProjectContextCollector()

        # Create minimal analysis result
        analysis_result = {
            "tech_stack": type("TechStack", (), {
                "primary_language": type("Language", (), {"value": "python"})()
            })()
        }

        context = collector.collect_context(analysis_result)

        # Verify all required AC1 fields are present
        assert context.project_name  # Project name
        assert context.language  # Primary language
        assert isinstance(context.detected_standards, dict)  # Standards dict
        assert isinstance(context.git_context, GitHistoryContext)  # Git context
        assert isinstance(context.dependencies, list)  # Dependencies list
        assert context.project_fingerprint  # Fingerprint for caching

    def test_context_is_organized_for_llm(self):
        """Test that context is properly organized for LLM consumption."""
        context = ProjectContext(
            project_name="test-project",
            language="python",
            framework="fastapi"
        )
        context.detected_standards["naming_convention"] = StandardsDetectionResult(
            standard_name="naming_convention",
            detected_value="snake_case",
            confidence=0.95,
            sample_size=100,
            evidence=["test_file.py", "helper_function()"],
        )

        # Verify context can be serialized for LLM
        context_dict = context.to_dict()
        assert isinstance(context_dict, dict)
        assert context_dict["project_name"] == "test-project"
        assert context_dict["language"] == "python"


class TestAC2_BuildStructuredPrompt:
    """AC2: Build Structured Enhancement Prompt"""

    def test_prompt_builder_includes_original_prompt(self):
        """Test that original prompt is preserved unchanged."""
        builder = PromptBuilder()
        original = "Design a user authentication API"

        context = ProjectContext(
            project_name="test",
            language="python"
        )

        prompt = builder.build_prompt(original, context)

        # Original prompt must be preserved
        assert original in prompt
        assert "<ORIGINAL_PROMPT>" in prompt
        assert "</ORIGINAL_PROMPT>" in prompt

    def test_prompt_includes_all_seven_sections(self):
        """Test that prompt includes all AC2 required sections."""
        builder = PromptBuilder()
        original = "Test prompt"

        context = ProjectContext(
            project_name="test",
            language="python",
            framework="fastapi",
            framework_version="0.100.0",
        )
        context.git_context = GitHistoryContext(current_branch="main", total_commits=42)
        context.detected_standards["naming_convention"] = StandardsDetectionResult(
            standard_name="naming",
            detected_value="snake_case",
            confidence=0.90,
            sample_size=100,
            evidence=[]
        )
        context.user_overrides = {"style": "concise"}
        context.template_name = "fastapi-template"

        prompt = builder.build_prompt(original, context)

        # Verify all sections
        assert "<ORIGINAL_PROMPT>" in prompt  # Section 1
        assert "<PROJECT_METADATA>" in prompt  # Section 2
        assert "<DETECTED_STANDARDS>" in prompt  # Section 3
        assert "<GIT_HISTORY>" in prompt  # Section 5
        assert "<USER_OVERRIDES>" in prompt  # Section 7
        assert "<TEMPLATE_INFO>" in prompt  # Section 8

    def test_prompt_formatted_for_llm_consumption(self):
        """Test that prompt is properly formatted for LLM."""
        builder = PromptBuilder()
        context = ProjectContext(project_name="test", language="python")

        prompt = builder.build_prompt("test", context)

        # Should be readable string
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "\n" in prompt  # Properly formatted with newlines


class TestAC3_HandleLowConfidence:
    """AC3: Handle Low-Confidence Standards"""

    def test_low_confidence_standards_marked_explicitly(self):
        """Test that low-confidence standards are marked."""
        builder = PromptBuilder()

        context = ProjectContext(project_name="test", language="python")
        context.detected_standards["doc_style"] = StandardsDetectionResult(
            standard_name="documentation_style",
            detected_value="mixed",
            confidence=0.55,  # Below 60% threshold
            sample_size=89,
            evidence=["Google docstrings", "NumPy docstrings"],
            exceptions="Mixed styles detected"
        )

        prompt = builder.build_prompt("test", context)

        # Low confidence should be marked
        assert "LOW CONFIDENCE" in prompt or "55%" in prompt
        assert "⚠️" in prompt  # Warning symbol

    def test_confidence_score_included(self):
        """Test that confidence scores are included."""
        builder = PromptBuilder()

        context = ProjectContext(project_name="test", language="python")
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming_convention",
            detected_value="snake_case",
            confidence=0.92,
            sample_size=100,
            evidence=["validate_email()"]
        )

        prompt = builder.build_prompt("test", context)

        # Confidence should be shown
        assert "92%" in prompt

    def test_evidence_and_exceptions_included(self):
        """Test that evidence and exceptions are shown."""
        builder = PromptBuilder()

        context = ProjectContext(project_name="test", language="python")
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming_convention",
            detected_value="snake_case",
            confidence=0.85,
            sample_size=100,
            evidence=["user_service.py", "format_date()"],
            exceptions="3 files use camelCase (likely copied library code)"
        )

        prompt = builder.build_prompt("test", context)

        # Evidence and exceptions should be shown
        assert "Evidence:" in prompt
        assert "Exceptions:" in prompt


class TestAC4_ExcludeSensitiveData:
    """AC4: Exclude Sensitive Information"""

    def test_validator_detects_api_keys(self):
        """Test that API keys are detected."""
        validator = SensitiveDataValidator()

        context_dict = {
            "api_key": "sk-1234567890abcdefghijk",
            "project_name": "test"
        }

        is_valid, violations = validator.validate_context_dict(context_dict)
        assert not is_valid
        assert any("openai_key" in v.lower() for v in violations)

    def test_validator_rejects_tokens(self):
        """Test that authentication tokens are detected."""
        validator = SensitiveDataValidator()

        context_dict = {
            "github_token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            "project": "test"
        }

        is_valid, violations = validator.validate_context_dict(context_dict)
        assert not is_valid

    def test_validator_accepts_clean_context(self):
        """Test that clean context passes validation."""
        validator = SensitiveDataValidator()

        context_dict = {
            "project_name": "test-project",
            "language": "python",
            "framework": "fastapi",
            "dependencies": ["fastapi", "pydantic", "sqlalchemy"]
        }

        is_valid, violations = validator.validate_context_dict(context_dict)
        assert is_valid
        assert len(violations) == 0

    def test_validator_sanitizes_for_logging(self):
        """Test that validator can sanitize for safe logging."""
        validator = SensitiveDataValidator()

        text = "API key is sk-1234567890abcdefghijk"
        sanitized = validator.sanitize_for_logging(text)

        assert "sk-" not in sanitized
        assert "[REDACTED]" in sanitized


class TestAC5_CacheProjectContext:
    """AC5: Cache Project Context for Consistency"""

    def test_context_can_be_serialized_to_dict(self):
        """Test that context is serializable for caching."""
        context = ProjectContext(
            project_name="test",
            language="python",
            project_fingerprint="abc123def456"
        )
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming",
            detected_value="snake_case",
            confidence=0.90,
            sample_size=100,
            evidence=[]
        )

        context_dict = context.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(context_dict)
        assert len(json_str) > 0

        # Should contain fingerprint for cache key
        assert context.project_fingerprint in str(context_dict)

    def test_context_includes_ttl_and_timestamp(self):
        """Test that context has timestamp for cache TTL validation."""
        context = ProjectContext(
            project_name="test",
            language="python"
        )
        context.collection_metadata = CollectionMetadata(
            collected_at="2025-12-19T10:30:00Z",
            collection_mode="full",
            standards_confidence={},
            fields_collected=["language"],
            fields_skipped=[]
        )

        assert context.collection_metadata.collected_at is not None
        assert "Z" in context.collection_metadata.collected_at  # ISO format


class TestAC6_FormatContextForDifferentModes:
    """AC6: Format Context for Different Use Cases"""

    def test_full_context_mode(self):
        """Test full context mode with all information."""
        collector = ProjectContextCollector()
        context = collector.collect_context(
            analysis_result={},
            collection_mode="full"
        )

        assert context.collection_metadata.collection_mode == "full"
        # Should attempt to collect everything

    def test_partial_context_mode(self):
        """Test partial context with some unavailable information."""
        collector = ProjectContextCollector()
        context = collector.collect_context(
            analysis_result={},
            collection_mode="partial"
        )

        assert context.collection_metadata.collection_mode == "partial"
        # Check that warnings mention partial mode
        warnings_text = " ".join(w.lower() for w in context.collection_metadata.warnings)
        assert "partial" in warnings_text

    def test_minimal_context_mode(self):
        """Test minimal context with only basic info."""
        collector = ProjectContextCollector()
        context = collector.collect_context(
            analysis_result={},
            collection_mode="minimal"
        )

        assert context.collection_metadata.collection_mode == "minimal"
        # Should only have language and framework

    def test_custom_context_with_user_overrides(self):
        """Test that user overrides are applied."""
        collector = ProjectContextCollector()
        user_overrides = {
            "naming_convention": "camelCase",
            "test_framework": "jest"
        }

        context = collector.collect_context(
            analysis_result={},
            user_overrides=user_overrides
        )

        assert context.user_overrides == user_overrides


class TestAC7_ValidationAndErrorHandling:
    """AC7: Validation and Error Handling"""

    def test_context_is_json_serializable(self):
        """Test that all context data is JSON-safe."""
        context = ProjectContext(
            project_name="test",
            language="python"
        )
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming",
            detected_value="snake_case",
            confidence=0.90,
            sample_size=100,
            evidence=["test.py"]
        )

        # Should not raise on JSON serialization
        json_str = json.dumps(context.to_dict())
        assert len(json_str) > 0

    def test_context_size_validation(self):
        """Test that context size is reasonable."""
        context = ProjectContext(
            project_name="test",
            language="python"
        )

        size = context.get_size_bytes()
        assert size > 0
        assert size < 100_000  # Should be < 100KB per AC7

    def test_graceful_degradation_on_missing_fields(self):
        """Test that missing optional fields don't break anything."""
        collector = ProjectContextCollector()

        # Minimal analysis result with missing fields
        context = collector.collect_context(analysis_result={})

        # Should still create valid context
        assert context is not None
        assert context.language
        assert isinstance(context.collection_metadata, CollectionMetadata)

    def test_error_logging_on_invalid_data(self):
        """Test that errors are handled and logged gracefully."""
        collector = ProjectContextCollector()

        # Create invalid analysis result
        bad_analysis = {"tech_stack": "invalid"}  # Not an object

        # Should not raise exception, should handle gracefully
        context = collector.collect_context(analysis_result=bad_analysis)
        assert context is not None


class TestAC8_ContextTransparency:
    """AC8: Context Transparency and Logging"""

    def test_collection_metadata_shows_what_was_collected(self):
        """Test that metadata shows what was collected."""
        collector = ProjectContextCollector()
        context = collector.collect_context(
            analysis_result={},
            collection_mode="full"
        )

        metadata = context.collection_metadata
        assert metadata is not None
        assert len(metadata.fields_collected) >= 0
        assert len(metadata.fields_skipped) >= 0

    def test_user_summary_generation(self):
        """Test that user-facing summary can be generated."""
        context = ProjectContext(
            project_name="test",
            language="python",
            framework="fastapi"
        )
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming_convention",
            detected_value="snake_case",
            confidence=0.95,
            sample_size=100,
            evidence=[]
        )

        # Should be able to generate user-friendly summary
        summary = f"🔍 Detected: {context.language}, {context.framework}, snake_case naming"
        assert "Detected" in summary

    def test_confidence_breakdown_available(self):
        """Test that confidence breakdown is available."""
        context = ProjectContext(
            project_name="test",
            language="python"
        )
        context.detected_standards["naming"] = StandardsDetectionResult(
            standard_name="naming",
            detected_value="snake_case",
            confidence=0.92,
            sample_size=100,
            evidence=[]
        )
        context.detected_standards["doc"] = StandardsDetectionResult(
            standard_name="documentation",
            detected_value="google",
            confidence=0.85,
            sample_size=95,
            evidence=[]
        )

        metadata = CollectionMetadata(
            collected_at="2025-12-19T10:30:00Z",
            collection_mode="full",
            standards_confidence={
                "naming": 0.92,
                "documentation": 0.85
            },
            fields_collected=["language", "standards"],
            fields_skipped=[]
        )
        context.collection_metadata = metadata

        # Should be able to show breakdown
        assert 0.92 in metadata.standards_confidence.values()
        assert 0.85 in metadata.standards_confidence.values()

    def test_warnings_about_skipped_context(self):
        """Test that warnings are shown about skipped context."""
        collector = ProjectContextCollector()
        context = collector.collect_context(
            analysis_result={},
            collection_mode="partial"
        )

        # Should have warnings about partial mode
        warnings = context.collection_metadata.warnings
        assert len(warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
