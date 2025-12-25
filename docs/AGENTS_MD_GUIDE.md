# AGENTS.md 使用指南

**版本**: 1.1.0
**日期**: 2025-12-15

---

## 什么是 AGENTS.md？

AGENTS.md 是一个为 AI 代理（如 Claude、GitHub Copilot 等）提供项目上下文的特殊文件。它作为"代理的 README"，告诉代理们：

- ✅ 如何在项目中工作
- ✅ 遵循哪些代码规范
- ✅ 有哪些边界和约束
- ✅ 需要注意的警告

**在 Prompt Enhancement 中**，AGENTS.md 是获取项目规范的**主要来源**，用于生成更准确、更符合项目风格的 prompt。

---

## 快速开始

### 第一步：在项目根目录创建 AGENTS.md

```bash
touch ./AGENTS.md
```

### 第二步：添加内容

选择以下两种格式之一：

#### 格式 A：结构化格式（推荐新项目）

```markdown
# Project Name - Development Guidelines

## Setup

Installation steps:

\`\`\`bash
pip install -r requirements.txt
pytest tests/ -v
\`\`\`

## Commands

Development commands:

\`\`\`bash
# Run tests
pytest tests/ -v --cov=src

# Run the application
python main.py

# Run linting
python -m flake8 src/
\`\`\`

## Code Style

- **Language**: Python 3.9+
- **Type Hints**: Required for all public functions
- **Naming Convention**: snake_case for functions/variables, PascalCase for classes
- **Line Length**: 88 characters (use Black formatter)
- **Docstrings**: Google-style format required

## Boundaries

Files and areas with restrictions:

- **Never modify**: `legacy/` directory without explicit approval
- **Deprecated**: `old_api()` → use `new_api()` instead
- **Requires approval**: Database migrations, security changes

## Testing

Test requirements:

- Minimum 80% code coverage
- All tests must pass: `pytest tests/ -v`
- Use pytest fixtures for test data

## Important Warnings

⚠️ Do NOT modify the `config.yaml` format without team discussion

🚨 Deprecated: UserService → use UserServiceV2 instead
```

#### 格式 B：灵活格式（官方标准）

```markdown
# Development Guide for Project

## Overview

This project uses Python 3.9+ with pytest for testing.

## Getting Started

To set up your environment:

\`\`\`bash
pip install -r requirements.txt
pip install pytest pytest-cov
\`\`\`

## Running Tests

\`\`\`bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
\`\`\`

## Code Conventions

We follow these practices:
- Use type hints for all functions
- Use snake_case for variables
- PascalCase for classes
- Maximum line length of 88 characters

## Important Notes

Never modify files in the legacy/ directory without approval.

Be careful with database migrations - always get explicit approval before running.

Deprecated APIs: Use NewAPI instead of OldAPI.
```

---

## 完整示例

### 结构化格式完整示例

```markdown
# Prompt Enhancement - Development Guidelines

## Setup

Initialize development environment:

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov black flake8

# Run tests to verify setup
pytest tests/ -v
\`\`\`

## Commands

### Development

\`\`\`bash
# Run the main tool
python main.py --prompt "your prompt here"

# Interactive mode
python main.py --interactive
\`\`\`

### Testing

\`\`\`bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent_docs_parser.py -v

# Run matching tests
pytest -k "test_parse" -v
\`\`\`

### Code Quality

\`\`\`bash
# Format code with Black
black src/ tests/

# Lint code
python -m flake8 src/ tests/

# Type checking
mypy src/
\`\`\`

## Code Style

### Naming Conventions

- **Functions & Variables**: `snake_case`
  - ✅ `get_user_id`, `max_attempts`
  - ❌ `getUserId`, `MaxAttempts`

- **Classes**: `PascalCase`
  - ✅ `AgentDocParser`, `ClarityScorer`
  - ❌ `agent_doc_parser`, `clarity_scorer`

- **Constants**: `UPPER_SNAKE_CASE`
  - ✅ `MAX_RETRIES`, `DEFAULT_TIMEOUT`
  - ❌ `max_retries`, `defaultTimeout`

### Type Hints

Type hints are **mandatory** for all public functions:

```python
# ✅ Good
def calculate_score(prompt: str, context: dict) -> float:
    """Calculate clarity score of a prompt.

    Args:
        prompt: User input prompt
        context: Project context information

    Returns:
        Clarity score between 0.0 and 1.0
    """
    ...

# ❌ Bad - No type hints
def calculate_score(prompt, context):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def parse_agents_md(file_path: str) -> AgentConfig:
    """Parse AGENTS.md file into structured config.

    Args:
        file_path: Path to AGENTS.md file

    Returns:
        AgentConfig containing parsed information

    Raises:
        FileNotFoundError: If file does not exist
        ParseError: If file cannot be parsed
    """
```

### Line Length

Maximum 88 characters (Black default):

```python
# ✅ Good - within limit
result = process_data(input_param, additional_param)

# ❌ Bad - exceeds limit
very_long_variable_name = some_very_long_function_name(param1, param2, param3)

# ✅ Good - line break for readability
result = process_data(
    input_param,
    additional_param,
    optional_param=True
)
```

## Boundaries & Constraints

### Protected Directories

Never modify these without explicit approval:

- `legacy/` - Legacy code, use at own risk
- `vendor/` - Third-party code, maintain integrity
- `.bmad/` - BMAD system files
- `archive/` - Historical code archive

### Deprecated APIs

When you see these, use the replacement:

| Old API | New API | Migration Guide |
|---------|---------|-----------------|
| `UserService.authenticate()` | `AuthManager.validate()` | See migration.md |
| `get_context()` | `ContextCollector.collect()` | New API returns dict |
| `format_prompt()` | `EnhancedPromptGenerator.generate()` | Upgrade to v1.1 |

### Requires Approval

These changes need explicit team approval:

- Database migrations
- Security-related changes
- API signature changes
- Configuration format changes

## Testing Requirements

### Minimum Standards

- **Coverage**: ≥ 80% code coverage
- **Tests**: All tests must pass before merge
- **Framework**: pytest
- **Fixtures**: Use pytest fixtures for test data

### Running Tests

```bash
# All tests with coverage
pytest tests/ --cov=src --cov-report=html

# Generate coverage report
# Open htmlcov/index.html to view

# Run specific test
pytest tests/test_agent_docs_parser.py::test_parse_structured
```

### Writing Tests

```python
import pytest
from agent_docs_parser import AgentDocParser


@pytest.fixture
def parser():
    """Fixture providing AgentDocParser instance"""
    return AgentDocParser()


@pytest.fixture
def sample_agents_md():
    """Fixture with sample AGENTS.md content"""
    return """
## Commands
npm run test

## Code Style
- Type hints required
"""


def test_parse_structured(parser, sample_agents_md):
    """Test parsing structured AGENTS.md"""
    config = parser.parse_from_content(sample_agents_md)
    assert len(config.commands) > 0
    assert len(config.guidelines) > 0
```

## Important Warnings

### ⚠️ Critical Warnings

**Do NOT modify config files without testing**
- Always test changes locally
- Run full test suite before committing
- Use feature branches for major changes

**Type safety is enforced**
- All functions must have type hints
- Use `mypy` for type checking
- Missing types will fail CI/CD

**Security considerations**
- Never commit API keys or secrets
- Use `.env` files for sensitive data
- Review security guidelines in `SECURITY.md`

### 🚨 Deprecated Patterns

These patterns are **DEPRECATED** and should not be used:

1. **Old service initialization**
   ```python
   # ❌ Deprecated
   service = OldUserService()

   # ✅ Use this instead
   manager = AuthManager()
   ```

2. **Old context API**
   ```python
   # ❌ Deprecated
   ctx = get_context()

   # ✅ Use this instead
   ctx = ContextCollector().collect(".")
   ```

3. **Old prompt generation**
   ```python
   # ❌ Deprecated
   prompt = format_prompt(input)

   # ✅ Use this instead
   enhanced = EnhancedPromptGenerator().generate(context)
   ```

## Version Information

### Current Version

- **Project**: Prompt Enhancement
- **Version**: 1.1.0
- **Python**: 3.9+
- **Framework**: None (library)

### Dependencies

```
PyYAML>=6.0
pydantic>=2.0
python-dotenv>=1.0
pytest>=7.0
pytest-cov>=4.0
```

## Contributing Guidelines

### Before You Start

1. Check this AGENTS.md for project guidelines
2. Run existing tests: `pytest tests/ -v`
3. Create a feature branch: `git checkout -b feature/your-feature`

### While Working

1. Follow code style (use Black formatter)
2. Add type hints to all new functions
3. Write tests for new functionality
4. Maintain ≥ 80% coverage

### Before Submitting PR

1. Run full test suite: `pytest tests/ --cov=src`
2. Format code: `black src/ tests/`
3. Lint code: `python -m flake8 src/`
4. Update CHANGELOG.md
5. Write clear commit messages

## FAQ

### Q: What should I put in AGENTS.md?

A: Include information that helps AI agents understand:
- How to set up the project
- Key commands to run
- Code style conventions
- Important constraints or deprecated APIs
- Testing requirements

### Q: Is AGENTS.md required?

A: No, but it's highly recommended. Without it:
- Agents have less context about your project
- Generated prompts may be less accurate
- Your project rules won't be enforced

### Q: Can I use markdown formatting?

A: Yes! AGENTS.md supports full markdown:
- Headings (#, ##, ###)
- Code blocks (bash, python, etc.)
- Lists and tables
- Bold, italic, links

### Q: How often should I update AGENTS.md?

A: Keep it updated when:
- You change project structure
- You add/remove commands
- You update dependencies
- You change coding standards
- You add new deprecated APIs

### Q: What format should I use?

A: Both formats are supported:
- **Structured**: Use if you want precise structure (## Commands, ## Code Style)
- **Flexible**: Use if you prefer natural markdown

Structured is easier for automated parsing, but flexible is more natural to write.

### Q: Can I have multiple AGENTS.md files?

A: In a monorepo, yes! Place AGENTS.md in each project subdirectory.

The parser uses "nearest file wins" - closest AGENTS.md to the edited file is used.

---

## Examples

### Minimal AGENTS.md (for small projects)

```markdown
# Quick Setup

\`\`\`bash
pip install -r requirements.txt
pytest tests/
\`\`\`

## Rules

- Type hints required
- 80% test coverage minimum
- Don't modify legacy/ without approval
```

### Comprehensive AGENTS.md (for larger projects)

See `examples/AGENTS.md.example` in the repository.

---

## Integration with Prompt Enhancement

When you have an AGENTS.md file:

```bash
# The /pe command automatically:
pe "add JWT authentication"

# 1. Finds your AGENTS.md
# 2. Parses it for rules and commands
# 3. Includes them in the enhanced prompt:
#    - Project Rules [from AGENTS.md]
#    - Boundaries ⚠️ [from AGENTS.md]
#    - Warnings 🚨 [from AGENTS.md]
# 4. Generates a more accurate response
```

---

## Best Practices

✅ **DO:**
- Keep AGENTS.md at project root
- Update it when rules change
- Include actual commands you use
- Use clear, concise language
- Include examples

❌ **DON'T:**
- Leave it outdated
- Include sensitive information
- Make it too long (keep < 500 lines)
- Use vague or unclear instructions
- Mix multiple projects in one file

---

**文档完成时间**: 2025-12-15
**兼容版本**: v1.1.0+
