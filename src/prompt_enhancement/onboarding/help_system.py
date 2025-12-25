"""Help system and template suggestion engine."""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class HelpSystem:
    """Provides help documentation at multiple levels of detail."""

    BASIC_HELP = """📚 Prompt Enhancement Help

🚀 Basic Usage:
  /pe "Your prompt"

  Example:
  /pe "How to implement user authentication?"

⚙️ Advanced Options:

  Configure Project Standards:
  /pe --override naming=camelCase "prompt"

  Use Templates:
  /pe --template fastapi "prompt"

  View Detected Standards:
  /pe --show-standards

📋 Available Templates:
  fastapi    - FastAPI Web Framework
  django     - Django Web Framework
  flask      - Flask Web Framework
  react      - React Application
  generic    - Generic Defaults

🔧 Commands:
  /pe-setup        - Initialize configuration
  /pe-help         - Show this help
  /pe-logs         - View diagnostic logs
  /pe-clear-cache  - Clear cached standards
  /pe-quickstart   - Show quick guide

💡 FAQ:
  Q: How do I change coding standards?
  A: Run /pe-setup or use --override flag

  Q: How do I save custom templates?
  A: After configuring standards, run /pe-save-template my-name

Need more help? Run /pe-help-full or check documentation"""

    FULL_HELP = """📖 Full Prompt Enhancement Documentation

## Commands

### /pe
Basic usage: /pe "your prompt"
Enhances prompts with project-aware guidance.

Options:
  --override SETTING=VALUE  - Override standard (multiple allowed)
  --template NAME           - Use predefined template
  --show-standards          - Display detected standards

### /pe-setup
Interactive setup wizard for initial configuration.
Prompts for API key, project type, and standards.

### /pe-help
Show basic help guide with common commands and templates.

### /pe-help-full
Show complete documentation with all details.

### /pe-help TOPIC
Show help for specific topic (standards, templates, config, examples, api, troubleshoot).

### /pe-logs
View diagnostic logs with filtering options.

### /pe-clear-cache
Clear cached standards detection results.

### /pe-quickstart
Show the 3-step quick guide for new users.

## Configuration

Configuration file: ~/.prompt-enhancement/config.yaml

```yaml
api_key: sk-...
project_type: python
naming_convention: snake_case
test_framework: pytest
documentation_style: google
code_organization: by-feature
first_time_setup_complete: true
```

## Standards Detection

The system automatically detects:
- Naming conventions (snake_case, camelCase, etc.)
- Test frameworks (pytest, jest, etc.)
- Documentation styles (google, numpy, jsdoc, etc.)
- Code organization patterns
- Module naming conventions

Detection runs on first execution and caches results.

## Template System

### Using Built-In Templates
/pe --template fastapi "your prompt"

### Creating Custom Templates
1. Configure standards with /pe-setup
2. Run: /pe-save-template my-template-name
3. Use: /pe --template my-template-name "prompt"

### Available Built-In Templates
- fastapi: FastAPI web framework standards
- django: Django web framework standards
- flask: Flask web framework standards
- react: React application standards
- generic: Generic defaults

## Troubleshooting

### "API Key Not Configured"
Run /pe-setup and enter your OpenAI API key.

### "Project Type Not Detected"
Ensure you're in the project root directory with identifying files (package.json, requirements.txt, etc.).

### "Low Confidence in Standards Detection"
Use --override flag to manually specify standards:
/pe --override naming=camelCase "prompt"

### "API Timeout"
Check internet connection and retry.

## Examples

### Basic enhancement
/pe "How to implement authentication in FastAPI?"

### With standards override
/pe --override naming=camelCase --override test_framework=jest "React component best practices"

### Using template
/pe --template django "Model design patterns"

### View detected standards
/pe --show-standards"""

    TOPIC_HELP = {
        "standards": """📋 Coding Standards

Available Standards:
- Naming Convention: snake_case, camelCase, PascalCase, kebab-case
- Test Framework: pytest, unittest, jest, mocha, NUnit, xUnit, TestNG, JUnit
- Documentation Style: google, numpy, sphinx, jsdoc, javadoc, pep257
- Code Organization: by-feature, by-layer, by-type, domain-driven, monolithic
- Module Naming Pattern: Custom patterns (e.g., service_, models_, etc.)

## How Detection Works
The system analyzes your project files to detect which standards are used.
It assigns confidence scores to each detected standard.

High confidence (≥85%): Multiple examples found
Medium confidence (60-85%): Some examples found
Low confidence (<60%): Few or conflicting examples

## How to Override
Use --override flag to set standards for a single run:
/pe --override naming=camelCase --override test_framework=jest "prompt"

## How to Configure Permanently
Run /pe-setup and specify your preferences, or edit config.yaml directly.""",
        "templates": """🎯 Template System

Built-in Templates:
- fastapi: FastAPI backend (snake_case, pytest, google docstrings, by-feature organization)
- django: Django backend (snake_case, pytest, google docstrings, by-layer organization)
- flask: Flask backend (snake_case, pytest, google docstrings, by-feature organization)
- react: React frontend (camelCase, jest, jsdoc comments, by-feature organization)
- generic: Generic defaults (no specific standards)

Using Templates:
/pe --template fastapi "your prompt"

Creating Custom Templates:
1. Configure standards using /pe-setup or --override
2. Save as template: /pe-save-template my-template
3. Use: /pe --template my-template "prompt"

Template Suggestions:
The system automatically suggests templates based on your project type.
When a template matches your project, you'll see a suggestion to use it.""",
        "config": """🔧 Configuration

Configuration File: ~/.prompt-enhancement/config.yaml

Example:
```yaml
api_key: sk-...
project_type: python
naming_convention: snake_case
test_framework: pytest
documentation_style: google
code_organization: by-feature
first_time_setup_complete: true
```

Keys:
- api_key: Your OpenAI API key
- project_type: Auto-detected or manually set
- naming_convention: Code naming convention
- test_framework: Testing framework used
- documentation_style: Documentation format
- code_organization: How code is organized
- first_time_setup_complete: Whether onboarding completed

Edit Directly:
You can edit config.yaml directly with your text editor.

Or Use Setup:
Run /pe-setup for interactive configuration.""",
        "examples": """💡 Usage Examples

### Basic Enhancement
/pe "How to implement user authentication?"

### With Override
/pe --override naming=camelCase "React component patterns"

### Using Template
/pe --template fastapi "How to create API endpoints?"

### Multiple Overrides
/pe --override naming=snake_case --override test_framework=unittest "Python async patterns"

### View Standards
/pe --show-standards

### Save Template
/pe-save-template my-project-template

### Interactive Setup
/pe-setup

### View Logs
/pe-logs

### Get Help
/pe-help
/pe-help-full
/pe-help standards
/pe-help templates""",
        "api": """🔑 API Key Setup

## Getting Your API Key

1. Visit https://platform.openai.com/account/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with sk-)
5. Keep it secret - don't share it

## Setting Your Key

### Interactive Setup
Run: /pe-setup
Follow the prompts to enter your API key.

### Manual Setup
Edit: ~/.prompt-enhancement/config.yaml
Add: api_key: sk-your-key-here

### Environment Variable
Export: export OPENAI_API_KEY=sk-your-key-here

## Troubleshooting

### Invalid Key
If you get "API key invalid", make sure:
- Key starts with "sk-"
- Key is copied completely (no extra spaces)
- Key is still active (not revoked)
- Your account has API access""",
        "troubleshoot": """🔧 Troubleshooting

### "API Key Not Configured"
Run: /pe-setup
Or set environment variable: export OPENAI_API_KEY=sk-...

### "Project Type Not Detected"
- Ensure you're in project root
- Add identifying files (package.json, requirements.txt, etc.)
- Use --override flag to manually set standards

### "Low Confidence in Standards Detection"
Use --override to manually specify:
/pe --override naming=camelCase --override test_framework=jest "prompt"

### "API Timeout"
Check internet connection and retry. API may be slow.

### "Permission Denied"
Some files couldn't be accessed. Check file permissions.

### "Enhancement Failed"
Check logs: /pe-logs
System degrades gracefully - you'll get generic enhancement.""",
    }

    @staticmethod
    def show_help(topic: Optional[str] = None) -> str:
        """
        Show help for specific topic or all help.

        Args:
            topic: Optional topic name

        Returns:
            Help text
        """
        if topic is None:
            return HelpSystem.BASIC_HELP

        topic = topic.lower().strip()

        if topic in HelpSystem.TOPIC_HELP:
            return HelpSystem.TOPIC_HELP[topic]
        else:
            return f"Unknown topic: {topic}\n\nAvailable topics: " + ", ".join(
                HelpSystem.TOPIC_HELP.keys()
            )

    @staticmethod
    def show_full_help() -> str:
        """
        Show full documentation.

        Returns:
            Full help text
        """
        return HelpSystem.FULL_HELP

    @staticmethod
    def show_basic_help() -> str:
        """
        Show basic help guide.

        Returns:
            Basic help text
        """
        return HelpSystem.BASIC_HELP

    @staticmethod
    def display_help(topic: Optional[str] = None, full: bool = False) -> None:
        """
        Display help to user.

        Args:
            topic: Optional specific topic
            full: Whether to show full help
        """
        if full:
            print(HelpSystem.show_full_help())
        else:
            print(HelpSystem.show_help(topic))


class TemplateSuggestion:
    """Suggests templates based on project type."""

    TEMPLATE_MAP = {
        "python": "fastapi",
        "nodejs": "react",
        "java": "generic",
        "go": "generic",
        "ruby": "generic",
    }

    @staticmethod
    def suggest_template(detected_project_type: Optional[str]) -> Optional[str]:
        """
        Suggest template based on project type.

        Args:
            detected_project_type: Detected project type

        Returns:
            Suggested template name or None
        """
        if not detected_project_type:
            return None

        project_type = detected_project_type.lower().strip()
        suggested = TemplateSuggestion.TEMPLATE_MAP.get(project_type)

        if suggested:
            logger.debug(f"Suggested {suggested} template for {project_type} project")

        return suggested

    @staticmethod
    def format_suggestion_prompt(
        detected_type: str,
        suggested_template: str,
    ) -> str:
        """
        Format template suggestion for display.

        Args:
            detected_type: The detected project type
            suggested_template: The suggested template name

        Returns:
            Formatted suggestion prompt
        """
        prompt = f"""
🎯 Recommended Template (based on your project):

Detected {detected_type} project
Recommended template: {suggested_template}

You can run:
  /pe --template {suggested_template} "your prompt"

Or create project configuration:
  /pe-setup

Continue? [Y/n]"""
        return prompt.strip()

    @staticmethod
    def show_suggestion(
        detected_type: str,
        suggested_template: str,
    ) -> bool:
        """
        Show suggestion and get user response.

        Args:
            detected_type: The detected project type
            suggested_template: The suggested template name

        Returns:
            True if user accepted, False if declined
        """
        prompt = TemplateSuggestion.format_suggestion_prompt(
            detected_type,
            suggested_template,
        )
        print(prompt)

        try:
            response = input().strip().lower()
            return response in ["y", "yes", ""]
        except (KeyboardInterrupt, EOFError):
            return False
