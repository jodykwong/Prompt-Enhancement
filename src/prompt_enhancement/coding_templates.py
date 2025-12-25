"""
Coding task template system for LLM enhancement.

Provides structured guidance, checklists, and best practices
for different types of coding tasks (implement, fix, refactor, test, review).
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml

logger = logging.getLogger(__name__)


@dataclass
class CodingTemplate:
    """Dataclass representing a coding task template."""

    name: str
    task_type: str
    description: str
    triggers: List[str]
    checklist: List[str]
    best_practices: Dict[str, List[str]]
    common_pitfalls: List[str]
    acceptance_criteria: List[str]
    examples: List[str]

    def __post_init__(self):
        """Validate template data after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        if not self.task_type or not isinstance(self.task_type, str):
            raise ValueError("task_type must be a non-empty string")
        if not isinstance(self.triggers, list) or not self.triggers:
            raise ValueError("triggers must be a non-empty list")


@dataclass
class TemplateMatch:
    """Result of template matching operation."""

    template: CodingTemplate
    trigger_word: str
    confidence: float

    def __post_init__(self):
        """Validate match data after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


class TemplateTrigger:
    """
    Template trigger word matcher.

    Matches user input against template triggers to identify
    the most appropriate template for a task.
    """

    def __init__(self):
        """Initialize the trigger matcher."""
        self.logger = logging.getLogger(__name__)

    def match(
        self,
        user_input: str,
        templates: List[CodingTemplate],
    ) -> Optional[TemplateMatch]:
        """
        Match user input to the most appropriate template.

        Args:
            user_input: User's task description
            templates: List of available templates

        Returns:
            TemplateMatch with best match or None if no match found
        """
        if not user_input or not templates:
            return None

        # Extract words from user input (case-insensitive)
        user_words = self._tokenize(user_input)

        # Calculate match scores for each template
        best_match = None
        best_score = 0.0

        for template in templates:
            score, trigger_word = self._calculate_match_score(
                user_words, template.triggers
            )

            if score > best_score:
                best_score = score
                best_match = (template, trigger_word, score)

        # Return match if confidence exceeds threshold (0.3)
        if best_match and best_match[2] >= 0.3:
            return TemplateMatch(
                template=best_match[0],
                trigger_word=best_match[1],
                confidence=best_match[2],
            )

        return None

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Supports both English and Chinese text.

        Args:
            text: Input text

        Returns:
            List of words/tokens
        """
        # Simple tokenization: split by spaces and punctuation
        # For Chinese, each character can be a token
        text_lower = text.lower()

        # Split by common delimiters
        import re

        words = re.findall(r"\w+", text_lower, re.UNICODE)

        return words

    def _calculate_match_score(
        self,
        user_words: List[str],
        template_triggers: List[str],
    ) -> tuple:
        """
        Calculate match score between user input and template triggers.

        Args:
            user_words: Tokenized user input
            template_triggers: Trigger words for template

        Returns:
            Tuple of (score, matched_trigger_word)
        """
        best_score = 0.0
        matched_trigger = ""

        for trigger in template_triggers:
            trigger_words = self._tokenize(trigger)

            # Check for exact word match
            for user_word in user_words:
                for trigger_word in trigger_words:
                    if user_word == trigger_word:
                        # Exact match: full score
                        return (1.0, trigger)

            # Check for partial match (substring)
            trigger_str = trigger.lower()
            for user_word in user_words:
                if user_word in trigger_str or trigger_str in user_word:
                    # Partial match: 0.6 score
                    if 0.6 > best_score:
                        best_score = 0.6
                        matched_trigger = trigger

        return (best_score, matched_trigger)


class CodingTemplateManager:
    """
    Manager for coding task templates.

    Loads, parses, and provides access to coding templates
    stored as YAML files.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template manager.

        Args:
            templates_dir: Path to templates directory
                          (defaults to src/prompt_enhancement/templates/)
        """
        self.logger = logging.getLogger(__name__)

        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to the templates directory in the package
            current_dir = Path(__file__).parent
            self.templates_dir = current_dir / "templates"

        self.templates: Dict[str, CodingTemplate] = {}
        self._template_files: Dict[str, Path] = {}  # Cache template file paths
        self.trigger_matcher = TemplateTrigger()
        self._cache: Dict[str, str] = {}
        self._templates_loaded = False  # Lazy loading flag
        self._template_index_loaded = False  # Index of available templates

    def _ensure_template_index(self) -> None:
        """
        Ensure template file index is loaded.

        Scans for template files but doesn't parse them yet.
        This is fast (file listing only, no parsing).
        """
        if self._template_index_loaded:
            return

        self._load_template_index()
        self._template_index_loaded = True

    def _load_template_index(self) -> None:
        """
        Build an index of available template files.

        Fast operation - just lists files, doesn't parse them.
        """
        if not self.templates_dir.exists():
            self.logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        yaml_files = self.templates_dir.glob("*.yaml")

        for yaml_file in yaml_files:
            # Extract task type from filename (implement.yaml -> implement)
            task_type = yaml_file.stem
            self._template_files[task_type] = yaml_file

        self.logger.debug(f"Indexed {len(self._template_files)} template files")

    def _ensure_templates_loaded(self) -> None:
        """
        Ensure all templates are loaded.

        Implements lazy loading - templates are only loaded when first needed,
        not during initialization. This improves startup performance.
        """
        if self._templates_loaded:
            return

        self._load_templates()
        self._templates_loaded = True

    def _load_templates(self) -> None:
        """Load all YAML template files from templates directory."""
        # First ensure index is loaded
        self._ensure_template_index()

        # Parse all indexed template files
        for task_type, yaml_file in self._template_files.items():
            if task_type not in self.templates:  # Skip already loaded
                try:
                    template = self._parse_yaml_template(yaml_file)
                    self.templates[template.task_type] = template
                    self.logger.debug(f"Loaded template: {template.task_type}")
                except Exception as e:
                    self.logger.error(f"Failed to load template {yaml_file}: {e}")

        self.logger.info(f"Loaded {len(self.templates)} templates")

    def _load_template_lazy(self, task_type: str) -> Optional[CodingTemplate]:
        """
        Load a single template on demand (lazy loading).

        Faster than loading all templates if only one is needed.
        """
        if task_type in self.templates:
            return self.templates[task_type]

        # Ensure index is loaded to find the file
        self._ensure_template_index()

        if task_type not in self._template_files:
            return None

        try:
            yaml_file = self._template_files[task_type]
            template = self._parse_yaml_template(yaml_file)
            self.templates[task_type] = template
            self.logger.debug(f"Lazy loaded template: {task_type}")
            return template
        except Exception as e:
            self.logger.error(f"Failed to load template {task_type}: {e}")
            return None

    def _parse_yaml_template(self, yaml_path: Path) -> CodingTemplate:
        """
        Parse a YAML template file into a CodingTemplate object.

        Args:
            yaml_path: Path to YAML file

        Returns:
            CodingTemplate object
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required_fields = [
            "name",
            "task_type",
            "description",
            "triggers",
            "checklist",
            "best_practices",
            "common_pitfalls",
            "acceptance_criteria",
            "examples",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return CodingTemplate(**data)

    def get_template(self, task_type: str) -> Optional[CodingTemplate]:
        """
        Get template by task type.

        Uses lazy loading for individual templates - only loads the requested
        template, not all templates.

        Args:
            task_type: Type of task (implement, fix, refactor, test, review)

        Returns:
            CodingTemplate or None
        """
        # Try lazy loading first (fast if only one template needed)
        if task_type in self.templates:
            return self.templates[task_type]

        return self._load_template_lazy(task_type)

    def match_template(self, user_input: str) -> Optional[TemplateMatch]:
        """
        Automatically match the most appropriate template.

        Args:
            user_input: User's task description

        Returns:
            TemplateMatch with matched template or None
        """
        self._ensure_templates_loaded()
        return self.trigger_matcher.match(user_input, list(self.templates.values()))

    def list_templates(self) -> List[str]:
        """
        List all available template task types.

        Returns:
            List of task type strings
        """
        self._ensure_templates_loaded()
        return list(self.templates.keys())

    def format_template(
        self,
        template: CodingTemplate,
        language: Optional[str] = None,
    ) -> str:
        """
        Format template as readable text.

        Args:
            template: CodingTemplate to format
            language: Programming language (optional, for filtering best practices)

        Returns:
            Formatted template text
        """
        # Check cache first (fast path)
        cache_key = f"{template.task_type}:{language or 'all'}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        output = []
        output.append(f"## {template.name}")
        output.append(f"\n{template.description}\n")

        # Checklist section
        output.append("\n### 📋 检查清单:")
        for item in template.checklist:
            output.append(f"- [ ] {item}")

        # Best practices section
        if language and language in template.best_practices:
            output.append(f"\n### ✨ {language.capitalize()}最佳实践:")
            for practice in template.best_practices[language]:
                output.append(f"- {practice}")
        else:
            output.append("\n### ✨ 最佳实践:")
            for lang, practices in template.best_practices.items():
                output.append(f"\n**{lang.capitalize()}**:")
                for practice in practices:
                    output.append(f"- {practice}")

        # Common pitfalls section
        output.append("\n### ⚠️ 常见陷阱:")
        for pitfall in template.common_pitfalls:
            output.append(f"- {pitfall}")

        # Acceptance criteria section
        output.append("\n### ✅ 验收标准:")
        for criterion in template.acceptance_criteria:
            output.append(f"- {criterion}")

        # Examples section
        if template.examples:
            output.append("\n### 📚 示例:")
            for example in template.examples:
                output.append(f"- {example}")

        formatted = "\n".join(output)

        # Cache the result
        self._cache[cache_key] = formatted

        return formatted

    def clear_cache(self) -> None:
        """Clear the format cache."""
        self._cache.clear()
        self.logger.debug("Template format cache cleared")
