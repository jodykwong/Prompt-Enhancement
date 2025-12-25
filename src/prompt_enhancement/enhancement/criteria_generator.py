"""
Verification criteria generator - generates project-specific verification criteria.

Implements AC2-AC5: Generate verification criteria, customize by project type,
add code examples, and include testing guidance.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from enum import Enum

from .context import ProjectContext
from .step_extractor import ImplementationStep

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Type of artifact that should be created/modified."""
    CODE_FILE = "code_file"
    TEST_FILE = "test_file"
    CONFIG_FILE = "config_file"
    DOCUMENTATION = "documentation"
    MIGRATION = "migration"
    BUILD_OUTPUT = "build_output"
    MANIFEST = "manifest"
    UNKNOWN = "unknown"


@dataclass
class VerificationCriterion:
    """Single verification criterion for a step (AC2)."""

    step_number: int  # Associated step
    criterion_type: str  # "artifact", "behavior", "code_review", "test"
    description: str  # What to verify
    artifact_type: Optional[ArtifactType] = None  # What artifact to check
    artifact_path_pattern: Optional[str] = None  # Where to find it (e.g., "src/**/*.py")
    expected_behavior: Optional[str] = None  # What should happen
    code_review_checklist: List[str] = field(default_factory=list)  # Code review items
    test_approach: Optional[str] = None  # How to test it
    success_indicator: str = ""  # How to know it worked


@dataclass
class CodeExample:
    """Code example following project standards (AC4)."""

    content: str  # Code content
    language: str  # Programming language
    filename_example: str  # Example filename
    follows_standards: Dict[str, str] = field(default_factory=dict)  # Which standards applied
    explanation: str = ""  # What the example shows
    project_type_note: str = ""  # Note about applicability


@dataclass
class TestingGuidance:
    """Testing guidance for a step (AC5)."""

    step_number: int  # Associated step
    framework: str  # Test framework name (pytest, unittest, etc)
    test_structure: str  # How to structure the test
    fixtures_needed: List[str] = field(default_factory=list)  # Required fixtures
    mocking_approach: str = ""  # How to mock dependencies
    assertion_style: str = ""  # Assertion format for this framework
    file_location: str = ""  # Where test file should go
    coverage_expectations: str = ""  # Coverage targets


@dataclass
class GeneratedCriteria:
    """Result of criteria generation (AC2)."""

    step: ImplementationStep  # Associated step
    verification_criteria: List[VerificationCriterion]  # Verification criteria
    code_examples: List[CodeExample] = field(default_factory=list)  # Code examples (AC4)
    testing_guidance: Optional[TestingGuidance] = None  # Testing guidance (AC5)
    common_pitfalls: List[str] = field(default_factory=list)  # Pitfalls to avoid
    debugging_tips: List[str] = field(default_factory=list)  # Debugging advice


class CriteriaGenerator:
    """
    Generates project-specific verification criteria for implementation steps.

    Implements AC2-AC5:
    - AC2: Generate specific verification criteria
    - AC3: Customize by project type
    - AC4: Add code examples following standards
    - AC5: Include testing guidance
    """

    def __init__(self, project_context: ProjectContext):
        """
        Initialize criteria generator with project context.

        Args:
            project_context: Project context from Story 3.1
        """
        self.context = project_context
        logger.debug(f"Initialized CriteriaGenerator for {project_context.project_name}")

    def generate_criteria_for_step(
        self,
        step: ImplementationStep,
        step_index: int = 0,
    ) -> GeneratedCriteria:
        """
        Generate verification criteria for a single implementation step.

        AC2: Generate specific criteria
        AC3: Customize by project type
        AC4: Include code examples
        AC5: Include testing guidance

        Args:
            step: Implementation step to generate criteria for
            step_index: Index in overall step sequence

        Returns:
            GeneratedCriteria with all verification components
        """
        logger.info(f"Generating criteria for step {step.number}: {step.content[:50]}...")

        # Generate base verification criteria (AC2)
        criteria = self._generate_verification_criteria(step, step_index)

        # Generate code examples (AC4)
        examples = self._generate_code_examples(step)

        # Generate testing guidance (AC5)
        testing = self._generate_testing_guidance(step, step_index)

        # Add pitfalls and debugging tips
        pitfalls = self._extract_pitfalls(step.content)
        tips = self._extract_debugging_tips(step.content)

        result = GeneratedCriteria(
            step=step,
            verification_criteria=criteria,
            code_examples=examples,
            testing_guidance=testing,
            common_pitfalls=pitfalls,
            debugging_tips=tips,
        )

        logger.debug(f"Generated {len(criteria)} criteria with {len(examples)} examples")
        return result

    def _generate_verification_criteria(
        self,
        step: ImplementationStep,
        step_index: int,
    ) -> List[VerificationCriterion]:
        """Generate specific verification criteria for a step (AC2)."""
        criteria = []
        step_num = step.number

        # Artifact criterion - what should be created/modified
        artifact = self._identify_artifact(step.content, step_index)
        if artifact:
            criteria.append(VerificationCriterion(
                step_number=step_num,
                criterion_type="artifact",
                description=f"Create or modify {artifact['name']}",
                artifact_type=artifact.get('type', ArtifactType.CODE_FILE),
                artifact_path_pattern=artifact.get('pattern'),
                success_indicator=f"{artifact['name']} exists at expected location",
            ))

        # Behavior criterion - what should happen
        behavior = self._identify_behavior(step.content)
        if behavior:
            criteria.append(VerificationCriterion(
                step_number=step_num,
                criterion_type="behavior",
                description=behavior['description'],
                expected_behavior=behavior['expected'],
                success_indicator=behavior.get('success_indicator', 'Feature works as expected'),
            ))

        # Code review criterion - following standards
        code_review = self._generate_code_review_checklist(step.content)
        if code_review:
            criteria.append(VerificationCriterion(
                step_number=step_num,
                criterion_type="code_review",
                description="Code review checklist",
                code_review_checklist=code_review,
                success_indicator="All code review items checked",
            ))

        # Ensure at least one criterion per step
        if not criteria:
            criteria.append(VerificationCriterion(
                step_number=step_num,
                criterion_type="behavior",
                description="Implementation complete",
                expected_behavior="Step implementation is complete and functional",
                success_indicator="Verify step produces expected result",
            ))

        return criteria

    def _identify_artifact(self, step_content: str, step_index: int) -> Optional[Dict]:
        """Identify what artifact should be created/modified (AC2)."""
        content_lower = step_content.lower()

        # Check for test file
        if any(word in content_lower for word in ["test", "unit test", "integration test"]):
            test_result = self.context.detected_standards.get("test_framework")
            framework = test_result.detected_value if test_result else "pytest"
            path_pattern = self._get_test_path_pattern(framework)
            return {
                'name': 'test file',
                'type': ArtifactType.TEST_FILE,
                'pattern': path_pattern,
            }

        # Check for configuration
        if any(word in content_lower for word in ["config", "configure", "settings", "environment"]):
            return {
                'name': 'configuration file',
                'type': ArtifactType.CONFIG_FILE,
                'pattern': '*.yaml/*.yml/*.json/*.toml',
            }

        # Check for documentation
        if any(word in content_lower for word in ["document", "readme", "docstring", "comment"]):
            return {
                'name': 'documentation',
                'type': ArtifactType.DOCUMENTATION,
                'pattern': '*.md/*.rst/*.txt',
            }

        # Default: code file
        return {
            'name': 'code file',
            'type': ArtifactType.CODE_FILE,
            'pattern': f'src/**/*.{self._get_file_extension()}',
        }

    def _identify_behavior(self, step_content: str) -> Optional[Dict]:
        """Identify expected behavior from step content (AC2)."""
        content_lower = step_content.lower()

        # Extract "should" statements or similar
        if "should" in content_lower or "will" in content_lower:
            # Find what should happen
            for phrase in ["should", "will"]:
                if phrase in content_lower:
                    idx = content_lower.index(phrase)
                    behavior_text = step_content[idx:idx+100].strip()
                    return {
                        'description': 'Verify expected behavior',
                        'expected': behavior_text,
                        'success_indicator': 'Behavior verified manually or through tests',
                    }

        # Default behavior
        return {
            'description': 'Verify implementation works correctly',
            'expected': step_content,
            'success_indicator': 'Step produces expected result',
        }

    def _generate_code_review_checklist(self, step_content: str) -> List[str]:
        """Generate code review checklist items following project standards (AC2)."""
        checklist = []

        # Always include: follows naming conventions
        naming_result = self.context.detected_standards.get("naming_conventions")
        naming = naming_result.detected_value if naming_result else "PEP 8"
        checklist.append(f"✓ Code follows {naming} naming conventions")

        # Include: proper imports and organization
        org_result = self.context.detected_standards.get("code_organization")
        org_pattern = org_result.detected_value if org_result else "by-layer"
        checklist.append(f"✓ Code organization matches project pattern ({org_pattern})")

        # Include: documentation
        doc_result = self.context.detected_standards.get("documentation_style")
        doc_style = doc_result.detected_value if doc_result else "Google"
        checklist.append(f"✓ Code includes {doc_style} style docstrings")

        # Include: error handling
        if "error" in step_content.lower() or "exception" in step_content.lower():
            checklist.append("✓ Error handling is implemented and tested")

        # Include: tests
        if "test" in step_content.lower():
            checklist.append("✓ Tests cover the new functionality")

        # Include: no hardcoded values
        checklist.append("✓ No hardcoded values or magic numbers")

        return checklist

    def _generate_code_examples(self, step: ImplementationStep) -> List[CodeExample]:
        """Generate code examples following project standards (AC4)."""
        examples = []

        # Determine language
        language = self.context.language
        framework = self.context.framework or "generic"

        # Create a basic example for the step
        example_code = self._create_example_code(step.content, language, framework)

        if example_code:
            naming_result = self.context.detected_standards.get("naming_conventions")
            org_result = self.context.detected_standards.get("code_organization")

            examples.append(CodeExample(
                content=example_code,
                language=language,
                filename_example=self._get_example_filename(step.content, language),
                follows_standards={
                    'naming': naming_result.detected_value if naming_result else 'default',
                    'organization': org_result.detected_value if org_result else 'default',
                    'language': language,
                    'framework': framework,
                },
                explanation=f"Example showing {step.content[:40]}...",
                project_type_note=f"[Example for {framework}]",
            ))

        return examples

    def _create_example_code(self, step_content: str, language: str, framework: str) -> Optional[str]:
        """Create code example following project standards (AC4)."""
        content_lower = step_content.lower()

        # Template examples for common patterns
        if "create" in content_lower and "function" in content_lower:
            if language == "python":
                return """def new_function(param1: str) -> str:
    \"\"\"Function description following Google style.

    Args:
        param1: Parameter description

    Returns:
        str: Return value description
    \"\"\"
    # Implementation here
    return result"""

        if "add" in content_lower and "endpoint" in content_lower:
            if framework in ["fastapi", "flask"]:
                return """@app.post("/endpoint")
async def create_item(item: Item) -> ItemResponse:
    \"\"\"Create a new item.

    Args:
        item: Item data

    Returns:
        ItemResponse: Created item
    \"\"\"
    # Implementation
    return ItemResponse(...)"""

        if "test" in content_lower:
            if language == "python":
                return """def test_new_feature():
    \"\"\"Test description.\"\"\"
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value"""

        # Generic fallback
        return None

    def _generate_testing_guidance(
        self,
        step: ImplementationStep,
        step_index: int,
    ) -> Optional[TestingGuidance]:
        """Generate testing guidance specific to project's test framework (AC5)."""
        # Only generate for implementation steps, not testing steps
        if "test" not in step.content.lower():
            return None

        test_result = self.context.detected_standards.get("test_framework")
        framework = test_result.detected_value if test_result else "pytest"
        language = self.context.language

        if language == "python" and framework == "pytest":
            return TestingGuidance(
                step_number=step.number,
                framework="pytest",
                test_structure="def test_feature_name(): # Arrange, Act, Assert",
                fixtures_needed=["fixture_name"] if "database" in step.content.lower() else [],
                mocking_approach="from unittest.mock import Mock, patch",
                assertion_style="assert result == expected",
                file_location=self._get_test_path_pattern(framework),
                coverage_expectations="Aim for 80%+ coverage",
            )

        if language == "python" and framework == "unittest":
            return TestingGuidance(
                step_number=step.number,
                framework="unittest",
                test_structure="class TestFeature(unittest.TestCase): def test_method(self):",
                fixtures_needed=[],
                mocking_approach="from unittest.mock import Mock, patch",
                assertion_style="self.assertEqual(result, expected)",
                file_location=self._get_test_path_pattern(framework),
                coverage_expectations="Aim for 80%+ coverage",
            )

        # Generic fallback
        return TestingGuidance(
            step_number=step.number,
            framework=framework,
            test_structure="Write tests following your framework's patterns",
            assertion_style="Use your framework's assertion methods",
            file_location=f"tests/test_*.{self._get_file_extension()}",
            coverage_expectations="Aim for 80%+ coverage",
        )

    def _extract_pitfalls(self, step_content: str) -> List[str]:
        """Extract common pitfalls for this step (AC6)."""
        pitfalls = []

        # Generic pitfalls that apply to most implementation
        pitfalls.extend([
            "Don't forget to handle error cases",
            "Ensure proper resource cleanup",
            "Validate all inputs before processing",
        ])

        # Context-specific pitfalls
        if "async" in step_content.lower():
            pitfalls.append("Remember to await async calls")
        if "database" in step_content.lower():
            pitfalls.append("Use connection pooling for database operations")
        if "api" in step_content.lower():
            pitfalls.append("Include proper timeout handling for API calls")

        return pitfalls

    def _extract_debugging_tips(self, step_content: str) -> List[str]:
        """Extract debugging tips for this step (AC6)."""
        tips = []

        # Generic tips
        tips.append("Enable debug logging to trace execution")
        tips.append("Use print statements or debugger to inspect values")

        # Context-specific tips
        if "data" in step_content.lower():
            tips.append("Inspect intermediate data structures with pprint or json.dumps")
        if "network" in step_content.lower() or "api" in step_content.lower():
            tips.append("Check network requests using curl or Postman")
        if "database" in step_content.lower():
            tips.append("Query database directly to verify data state")

        return tips

    def _get_test_path_pattern(self, framework: str) -> str:
        """Get expected test file path pattern for framework (AC5)."""
        if framework == "pytest":
            return "tests/test_*.py"
        elif framework == "unittest":
            return "tests/test_*.py"
        elif framework == "jest":
            return "src/**/*.test.js or src/**/*.spec.js"
        elif framework == "rspec":
            return "spec/**/*_spec.rb"
        else:
            return f"tests/test_*.{self._get_file_extension()}"

    def _get_file_extension(self) -> str:
        """Get file extension for project language."""
        language = (self.context.language or "").lower()
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "cpp": "cpp",
            "csharp": "cs",
            "ruby": "rb",
            "php": "php",
        }
        return extensions.get(language, "txt")

    def _get_example_filename(self, step_content: str, language: str) -> str:
        """Get example filename for code example (AC4)."""
        extension = self._get_file_extension()

        # Extract a keyword from step content
        words = step_content.split()
        keyword = "example" if len(words) < 2 else words[1].lower()
        keyword = "".join(c for c in keyword if c.isalnum())

        return f"{keyword}_example.{extension}"
