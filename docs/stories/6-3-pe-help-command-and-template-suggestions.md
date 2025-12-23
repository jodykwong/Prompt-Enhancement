# Story 6.3: `/pe-help` Command and Auto Template Suggestions

**Epic**: Epic 6: User Onboarding & Help System
**Priority**: High
**Acceptance Criteria**: 4
**Status**: Ready for Development

## Overview

Users should be able to access comprehensive help through `/pe-help` commands at multiple levels of detail, and the system should automatically suggest relevant templates based on detected project type.

## Acceptance Criteria

### AC1: Basic Help Command (/pe-help)

**Given** user runs `/pe-help` command
**When** requesting help
**Then** system displays basic help guide showing:
- Basic usage examples
- Available advanced options
- List of available templates
- Common commands
- FAQ section

**Example Output:**
```
📚 Prompt Enhancement Help

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

Need more help? Run /pe-help-full or check documentation
```

---

### AC2: Template Suggestion Based on Project

**Given** first run on detected project
**When** system analyzes project
**Then** system automatically suggests relevant template:

```
🎯 Recommended Template (based on your project):

Detected FastAPI project
Recommended template: fastapi

You can run:
  /pe --template fastapi "your prompt"

Or create project configuration:
  /pe-setup

Continue? [Y/n]
```

**Auto-Suggestion Logic:**
- Runs after project detection
- Only shows if clear match found
- Offers option to accept or skip
- Remembers preference for future runs

**Suggestion Timing:**
- On first `/pe` execution after project detection
- When running `/pe --show-standards` for first time
- When running `/pe-setup`

**User Actions:**
- [Y] Accept - Use template, remember preference
- [N] Decline - Skip suggestion, don't show again for this project
- [S] Skip - Don't use template this time, but ask again later

---

### AC3: Full Help Documentation (/pe-help-full)

**Given** user runs `/pe --help-full` or `/pe-help --full`
**When** requesting comprehensive help
**Then** system displays full documentation including:
- Detailed command reference
- Configuration file format
- Template system documentation
- Standards detection details
- Troubleshooting guide
- Examples for each feature

**Contents:**
```
📖 Full Prompt Enhancement Documentation

[Full detailed sections covering all features,
configuration options, examples, and troubleshooting]
```

**Help Sections Included:**
- Command Reference (detailed)
- Configuration File Format (YAML structure)
- Template System (creating, using, managing)
- Standards Detection (how it works)
- API Key Setup (detailed)
- Troubleshooting (common issues and solutions)
- Advanced Features (for power users)

---

### AC4: Topic-Specific Help

**Given** user looking for specific information
**When** using help with topic filter
**Then** system displays topic-specific help:

**Available Topics:**
- `/pe-help standards` - Coding standards details
- `/pe-help templates` - Template system details
- `/pe-help config` - Configuration file details
- `/pe-help examples` - Usage examples
- `/pe-help api` - API key setup details
- `/pe-help troubleshoot` - Troubleshooting guide

**Example: `/pe-help standards`**
```
📋 Coding Standards

Available Standards:
- Naming Convention (snake_case, camelCase, etc.)
- Test Framework (pytest, jest, unittest, etc.)
- Documentation Style (google, numpy, jsdoc, etc.)
- Code Organization (by-feature, by-layer, etc.)
- Module Naming Pattern (custom patterns)

How Detection Works:
[Detailed explanation of how standards are detected]

How to Override:
[Examples of using --override flag]

How to Configure:
[Examples of config file setup]
```

---

## Technical Requirements

### Help Display System

```python
class HelpSystem:
    def show_help(self, topic: Optional[str] = None) -> str:
        """Show help for specific topic or all help."""

    def show_basic_help(self) -> str:
        """Show basic help guide."""

    def show_full_help(self) -> str:
        """Show full documentation."""

    def show_topic_help(self, topic: str) -> str:
        """Show help for specific topic."""
```

### Template Suggestion Engine

```python
class TemplateSuggestion:
    def suggest_template(self, detected_project_type: str) -> Optional[str]:
        """Suggest template based on project type."""

    def format_suggestion_prompt(self, template_name: str) -> str:
        """Format template suggestion for display."""
```

### Project Type to Template Mapping

```python
TEMPLATE_SUGGESTIONS = {
    "python": "fastapi or django",
    "nodejs": "react",
    "java": "generic",
    "go": "generic",
    "ruby": "generic",
}
```

---

## Testing Strategy

### Unit Tests

- **test_basic_help_displayed**: Basic help shows all sections
- **test_basic_help_has_usage**: Help includes usage examples
- **test_basic_help_has_templates**: Help lists all templates
- **test_basic_help_has_commands**: Help lists all commands
- **test_basic_help_has_faq**: Help includes FAQ
- **test_full_help_comprehensive**: Full help covers all topics
- **test_topic_help_standards**: Standards help complete
- **test_topic_help_templates**: Templates help complete
- **test_topic_help_config**: Config help complete
- **test_topic_help_examples**: Examples help complete
- **test_template_suggestion_fastapi**: FastAPI project suggested correctly
- **test_template_suggestion_django**: Django project suggested correctly
- **test_template_suggestion_react**: React project suggested correctly
- **test_suggestion_format**: Suggestion prompt formatted correctly
- **test_suggestion_memory**: Suggestion preference remembered
- **test_invalid_topic**: Invalid topic shows error

### Integration Tests

- **test_full_help_workflow**: User gets help and understands options
- **test_template_suggestion_workflow**: Suggestion shown and can accept/decline
- **test_help_topic_consistency**: All topics are consistent in style

---

## Definition of Done

- [ ] HelpSystem class created with all help levels
- [ ] Basic help (/pe-help) implemented and formatted
- [ ] Full help (/pe-help-full) implemented
- [ ] Topic-specific help implemented for all topics
- [ ] Template suggestion engine created
- [ ] Auto-suggestion on first run working
- [ ] User can accept/decline/skip suggestions
- [ ] Suggestion preference remembered
- [ ] All help text properly formatted with emojis
- [ ] Help links accurate and helpful
- [ ] All 4 AC implemented and tested
- [ ] 16+ unit tests all passing
- [ ] Code review approved
- [ ] Story file updated to DONE

