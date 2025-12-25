# Day 1 启动指南 - Agent Docs Parser 实现

**日期**: 2025-12-16 (Tomorrow!)
**目标**: Agent Docs Parser 完整可用 + 单元测试通过
**工作量**: 6-7小时
**验收标准**: ✅ 所有测试通过 + 覆盖率≥85%

---

## 时间表

```
09:00-09:30  团队启动会 (15m)        → 确认分工
09:30-10:00  开发环境检查 (30m)      → 准备就绪
────────────────────────────────────────
10:00-11:00  Task 1.1: 项目结构 (1h)
11:00-12:00  Task 1.2: 数据模型 (1h)
12:00-13:00  午休
13:00-15:00  Task 1.3: 核心实现 (2h)
15:00-16:00  Task 1.4: 单元测试 (1.5h)
────────────────────────────────────────
16:00-16:30  Code Review (30m)       → 架构师审查
16:30-17:00  问题修复 + 总结 (30m)
17:30+       Day 1 deliverable 完成
```

---

## 任务分解

### ✅ 准备工作（今天下午或明早）

在Day 1启动前，确保：

```bash
# 1. 检查分支状态
git branch -a  # 确认在 feature/v1.1-brownfield

# 2. 确认项目结构
ls -la src/v1_1/     # 应该存在
ls -la tests/v1_1/   # 应该存在

# 3. 虚拟环境检查
python3 --version    # >= 3.8
which python3        # 确认venv激活

# 4. 依赖检查
pip list | grep pytest
pip list | grep black
pip list | grep mypy
```

### Task 1.1：创建项目结构（1h）

**当前状态**: ✅ 已完成 (由Claude完成)

**验证**:
```bash
ls -R src/v1_1/
# 应该看到:
# src/v1_1/__init__.py
```

**下一步**: 检查无误，继续1.2

---

### Task 1.2：定义数据模型（1h）

**文件**: `src/v1_1/models.py`

**内容** (按这个框架实现):

```python
"""
Data models for Prompt Enhancement v1.1

This module defines all data classes used in the v1.1 pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class CodeBlock:
    """Code block extracted from AGENTS.md"""
    language: str                 # bash, python, js, etc.
    content: str                  # code content
    line_number: int              # line number in source file


@dataclass
class AgentConfig:
    """Unified representation of parsed AGENTS.md"""

    # Source info
    source_file: str = ""         # path to source file
    format_type: str = ""         # "structured" or "flexible"
    raw_content: str = ""         # original file content

    # Extracted content
    commands: List[str] = field(default_factory=list)
    guidelines: List[str] = field(default_factory=list)
    boundaries: Dict[str, List] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    testing: Dict[str, str] = field(default_factory=dict)

    # Sections and code blocks
    sections: Dict[str, str] = field(default_factory=dict)
    code_blocks: List[CodeBlock] = field(default_factory=list)

    # Metadata
    last_modified: Optional[datetime] = None
    parse_errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if config has valid content"""
        return bool(
            self.commands or
            self.guidelines or
            self.boundaries or
            self.warnings
        )

    @classmethod
    def empty(cls) -> "AgentConfig":
        """Create an empty config"""
        return cls()


@dataclass
class EnhancementContext:
    """Complete enhancement context for prompt generation"""

    # Original input
    user_prompt: str = ""

    # Agent configuration
    agents_config: AgentConfig = field(default_factory=AgentConfig)

    # Clarity assessment
    clarity_score: float = 0.5
    clarity_level: str = "medium"  # clear / medium / unclear

    # Project context (existing from v1.01)
    tech_stack: Dict = field(default_factory=dict)
    project_structure: Dict = field(default_factory=dict)
    git_history: Dict = field(default_factory=dict)

    # Cache info
    cache_hit: bool = False
    cache_age_seconds: Optional[int] = None


@dataclass
class EnhancedPrompt:
    """Enhanced prompt output"""

    # Original info
    original_prompt: str = ""
    clarity_score: float = 0.5

    # v1.1 new sections
    project_norms: str = ""              # from AGENTS.md commands/guidelines
    boundary_constraints: str = ""       # ⚠️ from AGENTS.md boundaries
    special_warnings: str = ""           # 🚨 from AGENTS.md warnings

    # Existing sections
    project_context: str = ""
    relevant_files: str = ""
    code_snippets: str = ""
    best_practices: str = ""

    # Metadata
    generation_time_ms: float = 0.0
    cache_hit: bool = False
    agents_config_source: str = ""
```

**验收标准**:
- ✅ 所有@dataclass都有proper初始化
- ✅ 所有字段都有type hints
- ✅ AgentConfig.is_valid() 方法工作
- ✅ 可以创建实例: `config = AgentConfig()`

**预计时间**: 1小时

---

### Task 1.3：Agent Docs Parser 核心实现（2h）

**文件**: `src/v1_1/agent_docs_parser.py`

**主要内容**:

```python
"""
Agent Docs Parser - Parse AGENTS.md files with dual format support

Supports both structured (## Section) and flexible (natural) markdown formats.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from .models import AgentConfig, CodeBlock


logger = logging.getLogger(__name__)


class AgentDocParser:
    """Parser for AGENTS.md / CLAUDE.md configuration files"""

    SEARCH_PATHS = [
        "./AGENTS.md",
        "./CLAUDE.md",
        "./.github/copilot-instructions.md",
    ]

    SECTION_KEYWORDS = {
        "commands": ["command", "setup", "installation", "run", "bash"],
        "guidelines": ["code style", "convention", "guideline", "best practice"],
        "boundaries": ["never", "avoid", "don't", "boundary", "constraint"],
        "warnings": ["warning", "caution", "important", "deprecated"],
        "testing": ["test", "testing", "validation", "qa"],
    }

    def find_config_file(
        self,
        project_root: str,
        force_source: Optional[str] = None
    ) -> Optional[str]:
        """
        Find AGENTS.md file in project

        Args:
            project_root: Project root directory
            force_source: Force specific config file

        Returns:
            Path to config file or None

        Raises:
            FileNotFoundError: If forced file not found
        """
        if force_source:
            path = os.path.join(project_root, force_source)
            if os.path.exists(path):
                return path
            raise FileNotFoundError(f"Config {force_source} not found")

        found_configs = []
        for search_path in self.SEARCH_PATHS:
            full_path = os.path.join(project_root, search_path)
            if os.path.exists(full_path):
                found_configs.append((search_path, full_path))

        if not found_configs:
            logger.debug(f"No config files found in {project_root}")
            return None

        if len(found_configs) > 1:
            logger.warning(
                f"Found multiple config files: "
                f"{[p[0] for p in found_configs]}. "
                f"Using {found_configs[0][0]}"
            )

        return found_configs[0][1]

    def parse(self, file_path: str) -> AgentConfig:
        """
        Parse AGENTS.md file

        Args:
            file_path: Path to config file

        Returns:
            AgentConfig object
        """
        try:
            content = self._read_file(file_path)
            format_type = self.detect_format(content)

            if format_type == "structured":
                config = self._parse_structured_format(content)
            else:
                config = self._parse_flexible_format(content)

            config.source_file = file_path
            config.format_type = format_type
            config.raw_content = content
            config.last_modified = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )

            return config
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return AgentConfig.empty()

    def detect_format(self, content: str) -> str:
        """
        Detect format type (structured vs flexible)

        Args:
            content: File content

        Returns:
            "structured" or "flexible"
        """
        structured_markers = [
            "## Commands",
            "## Code Style",
            "## Boundaries",
            "## Warnings",
            "## Testing",
        ]

        if any(marker in content for marker in structured_markers):
            return "structured"
        return "flexible"

    def _parse_structured_format(self, content: str) -> AgentConfig:
        """Parse structured format with ## sections"""
        config = AgentConfig()
        sections = self._split_by_heading(content, level=2)

        for section_name, section_content in sections.items():
            section_lower = section_name.lower()

            if "command" in section_lower:
                config.commands = self._extract_commands(section_content)
            elif "style" in section_lower or "guideline" in section_lower:
                config.guidelines = self._extract_guidelines(section_content)
            elif "boundar" in section_lower:
                config.boundaries = self._extract_boundaries(section_content)
            elif "warning" in section_lower:
                config.warnings = self._extract_warnings(section_content)
            elif "test" in section_lower:
                config.testing = self._extract_testing(section_content)

            config.sections[section_name] = section_content

        config.code_blocks = self._extract_all_code_blocks(content)
        return config

    def _parse_flexible_format(self, content: str) -> AgentConfig:
        """Parse flexible format with keyword inference"""
        config = AgentConfig()

        config.code_blocks = self._extract_all_code_blocks(content)
        config.commands = self._infer_commands(content)
        config.guidelines = self._infer_guidelines(content)
        config.boundaries = self._infer_boundaries(content)
        config.warnings = self._infer_warnings(content)
        config.testing = self._infer_testing(content)
        config.sections = self._split_by_heading(content, level=1)

        return config

    # Helper methods...
    def _extract_commands(self, section: str) -> List[str]:
        """Extract commands from section"""
        commands = []
        code_blocks = re.findall(
            r'```(?:bash|shell|sh)?\n(.*?)\n```',
            section,
            re.DOTALL
        )

        for block in code_blocks:
            for line in block.split('\n'):
                line = line.strip()
                if any(line.startswith(cmd) for cmd in
                       ['npm ', 'yarn ', 'pip ', 'python ', 'pytest ']):
                    commands.append(line)

        return commands

    def _extract_guidelines(self, section: str) -> List[str]:
        """Extract guidelines from section"""
        guidelines = []
        bullets = re.findall(r'^[\s]*[-*+]\s+(.+?)$', section, re.MULTILINE)
        guidelines.extend(bullets)
        bold = re.findall(r'\*\*(.+?)\*\*', section)
        guidelines.extend(bold)
        return guidelines

    def _extract_warnings(self, section: str) -> List[str]:
        """Extract warnings from section"""
        warnings = []
        paragraphs = section.split('\n\n')
        for para in paragraphs:
            if any(kw in para.lower() for kw in
                   ['warning', 'caution', 'important']):
                warnings.append(para.strip())
        return warnings

    def _extract_boundaries(self, section: str) -> Dict[str, List]:
        """Extract boundaries from section"""
        boundaries = {
            "never_modify": [],
            "require_approval": [],
            "deprecated": []
        }
        bullets = re.findall(r'^[\s]*[-*+]\s+(.+?)$', section, re.MULTILINE)

        for bullet in bullets:
            if "never" in bullet.lower() or "don't" in bullet.lower():
                boundaries["never_modify"].append(bullet)
            elif "approval" in bullet.lower():
                boundaries["require_approval"].append(bullet)
            elif "deprecated" in bullet.lower():
                boundaries["deprecated"].append(bullet)

        return boundaries

    def _extract_testing(self, section: str) -> Dict[str, str]:
        """Extract testing config from section"""
        testing = {}
        commands = self._extract_commands(section)
        if commands:
            testing["commands"] = commands

        if "coverage" in section.lower():
            match = re.search(r'coverage.*?(\d+)%', section, re.IGNORECASE)
            if match:
                testing["coverage_threshold"] = match.group(1)

        return testing

    def _infer_commands(self, content: str) -> List[str]:
        """Infer commands from flexible format"""
        commands = []
        code_blocks = self._extract_all_code_blocks(content)

        for block in code_blocks:
            if block.language in ['bash', 'shell', 'sh']:
                for line in block.content.split('\n'):
                    line = line.strip()
                    if any(line.startswith(cmd) for cmd in
                           ['npm ', 'yarn ', 'pip ', 'python ']):
                        commands.append(line)

        return commands

    def _infer_guidelines(self, content: str) -> List[str]:
        """Infer guidelines from flexible format"""
        guidelines = []
        bullets = re.findall(r'^[\s]*[-*+]\s+(.+?)$', content, re.MULTILINE)
        guidelines.extend(bullets)
        emphasized = re.findall(r'\*\*(.+?)\*\*|_(.+?)_', content)
        for group in emphasized:
            guidelines.extend([item for item in group if item])
        return guidelines

    def _infer_warnings(self, content: str) -> List[str]:
        """Infer warnings from flexible format"""
        warnings = []
        warning_keywords = ['warning', 'caution', 'never', 'avoid',
                           'deprecated', '⚠️', '🚨']
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if any(kw.lower() in para.lower() for kw in warning_keywords):
                warnings.append(para.strip())
        return warnings

    def _infer_boundaries(self, content: str) -> Dict[str, List]:
        """Infer boundaries from flexible format"""
        boundaries = {"never_modify": [], "require_approval": []}
        lines = content.split('\n')
        for line in lines:
            if "never" in line.lower() or "don't" in line.lower():
                boundaries["never_modify"].append(line.strip())
            elif "approval" in line.lower():
                boundaries["require_approval"].append(line.strip())
        return boundaries

    def _infer_testing(self, content: str) -> Dict[str, str]:
        """Infer testing config from flexible format"""
        testing = {}
        frameworks = ["pytest", "unittest", "jest", "mocha"]
        for fw in frameworks:
            if fw in content.lower():
                testing["framework"] = fw
                break

        match = re.search(r'coverage.*?(\d+)%', content, re.IGNORECASE)
        if match:
            testing["coverage_threshold"] = match.group(1)

        return testing

    def _extract_all_code_blocks(self, content: str) -> List[CodeBlock]:
        """Extract all code blocks from content"""
        code_blocks = []
        pattern = r'```([\w]*)\n(.*?)\n```'

        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or "text"
            code_content = match.group(2)
            line_number = content[:match.start()].count('\n') + 1

            code_blocks.append(CodeBlock(
                language=language,
                content=code_content,
                line_number=line_number
            ))

        return code_blocks

    def _split_by_heading(
        self,
        content: str,
        level: int = 2
    ) -> Dict[str, str]:
        """Split content by heading level"""
        sections = {}
        heading_pattern = f"^{'#' * level} "

        current_section = None
        current_content = []

        for line in content.split('\n'):
            if re.match(heading_pattern, line):
                if current_section:
                    sections[current_section] = '\n'.join(
                        current_content
                    ).strip()
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
```

**验收标准**:
- ✅ 类结构完整
- ✅ find_config_file() 工作正常
- ✅ detect_format() 能区分两种格式
- ✅ parse() 返回有效的AgentConfig
- ✅ 缺失文件返回empty config而非crash
- ✅ 所有辅助方法都实现了

**预计时间**: 2小时

---

### Task 1.4：单元测试（1.5h）

**文件**: `tests/v1_1/test_agent_docs_parser.py`

**基本测试框架**:

```python
"""
Unit tests for Agent Docs Parser
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.v1_1.agent_docs_parser import AgentDocParser
from src.v1_1.models import AgentConfig


@pytest.fixture
def parser():
    """Create parser instance"""
    return AgentDocParser()


@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestFindConfigFile:
    """Test find_config_file method"""

    def test_find_agents_md(self, parser, temp_dir):
        """Test finding AGENTS.md"""
        # Create AGENTS.md
        agents_path = os.path.join(temp_dir, "AGENTS.md")
        Path(agents_path).write_text("# Test")

        # Find it
        found = parser.find_config_file(temp_dir)
        assert found == agents_path

    def test_find_claude_md(self, parser, temp_dir):
        """Test finding CLAUDE.md as fallback"""
        claude_path = os.path.join(temp_dir, "CLAUDE.md")
        Path(claude_path).write_text("# Test")

        found = parser.find_config_file(temp_dir)
        assert found == claude_path

    def test_no_config_file(self, parser, temp_dir):
        """Test when no config file exists"""
        found = parser.find_config_file(temp_dir)
        assert found is None

    def test_force_source_exists(self, parser, temp_dir):
        """Test forcing specific source"""
        agents_path = os.path.join(temp_dir, "AGENTS.md")
        Path(agents_path).write_text("# Test")

        found = parser.find_config_file(temp_dir, force_source="AGENTS.md")
        assert found == agents_path

    def test_force_source_not_exists(self, parser, temp_dir):
        """Test forcing non-existent source"""
        with pytest.raises(FileNotFoundError):
            parser.find_config_file(temp_dir, force_source="MISSING.md")


class TestDetectFormat:
    """Test format detection"""

    def test_structured_format(self, parser):
        """Test structured format detection"""
        content = """# Title
## Commands
```bash
npm install
```
## Code Style
- Use type hints
"""
        assert parser.detect_format(content) == "structured"

    def test_flexible_format(self, parser):
        """Test flexible format detection"""
        content = """# My Project Rules
This is a flexible format with no explicit sections.
```bash
npm test
```
Important: Never modify X
"""
        assert parser.detect_format(content) == "flexible"


class TestParse:
    """Test parse method"""

    def test_parse_structured(self, parser, temp_dir):
        """Test parsing structured format"""
        agents_path = os.path.join(temp_dir, "AGENTS.md")
        content = """## Commands
```bash
npm install
pytest tests/
```
## Code Style
- Use type hints
- snake_case for functions
## Warnings
⚠️ Never modify legacy code
"""
        Path(agents_path).write_text(content)

        config = parser.parse(agents_path)

        assert config.source_file == agents_path
        assert config.format_type == "structured"
        assert len(config.commands) > 0
        assert len(config.guidelines) > 0
        assert config.is_valid

    def test_parse_missing_file(self, parser, temp_dir):
        """Test parsing missing file"""
        missing_path = os.path.join(temp_dir, "MISSING.md")
        config = parser.parse(missing_path)

        assert not config.is_valid
        assert config.source_file == ""


class TestExtraction:
    """Test extraction methods"""

    def test_extract_bash_commands(self, parser):
        """Test bash command extraction"""
        content = """
```bash
npm install
pytest tests/ -v
python setup.py install
```
"""
        commands = parser._extract_commands(content)
        assert "npm install" in commands
        assert "pytest tests/ -v" in commands

    def test_extract_guidelines(self, parser):
        """Test guideline extraction"""
        content = """
- Use type hints
- Follow PEP 8
- **Never modify config files**
"""
        guidelines = parser._extract_guidelines(content)
        assert len(guidelines) > 0

    def test_extract_warnings(self, parser):
        """Test warning extraction"""
        content = """
⚠️ Warning: Never modify this file

Important: Always run tests before commit
"""
        warnings = parser._extract_warnings(content)
        assert len(warnings) > 0
```

**验收标准**:
- ✅ 6个测试类通过
- ✅ 所有关键路径都有测试
- ✅ 错误情况都覆盖了
- ✅ 覆盖率 >= 85%

**运行测试**:
```bash
pytest tests/v1_1/test_agent_docs_parser.py -v
pytest tests/v1_1/ -v --cov=src/v1_1 --cov-report=term-missing
```

**预计时间**: 1.5小时

---

## Code Review Checklist (16:00)

架构师审查时使用：

```yaml
代码质量:
  [ ] 命名清晰易懂
  [ ] 没有复杂的嵌套 (> 3层)
  [ ] 函数大小合理 (< 30行为佳)
  [ ] 类的单一责任

错误处理:
  [ ] 所有异常都被捕获
  [ ] 异常信息有用
  [ ] 优雅降级（缺失文件返回empty）

类型提示:
  [ ] 所有函数都有完整的类型提示
  [ ] 返回类型明确
  [ ] Optional 使用正确

文档:
  [ ] 每个类都有docstring
  [ ] 每个public方法都有docstring
  [ ] Docstring包含Args/Returns

测试:
  [ ] 单元测试覆盖主要路径
  [ ] 覆盖率 >= 85%
  [ ] 测试命名清晰
  [ ] 没有flaky tests
```

---

## 遇到问题？

### 问题：代码导入错误
```bash
# 解决: 确保在项目根目录运行
cd /path/to/Prompt-Enhancement
python -m pytest tests/v1_1/
```

### 问题：测试覆盖率不足
```bash
# 分析: 看哪些行没被覆盖
pytest tests/v1_1/ --cov=src/v1_1 --cov-report=html
# 在htmlcov/index.html中查看
```

### 问题：代码审查反馈多
```bash
# 常见issue:
1. 缺少错误处理 → 加try/except
2. 缺少type hints → 加上:类型
3. 复杂逻辑 → 拆分到小函数
4. 文档不清 → 改进docstring
```

---

## Day 1 完成标志 ✅

```
[ ] Task 1.1: 项目结构创建 ✓ (已由Claude完成)
[ ] Task 1.2: 数据模型定义 - 完成
[ ] Task 1.3: Agent Parser 核心 - 完成
[ ] Task 1.4: 单元测试 - 完成
[ ] Code Review 通过 - 通过
[ ] 所有测试运行通过 - 绿色
[ ] 覆盖率 >= 85% - 达成
[ ] 无lint错误 - clean
[ ] 文档完整 - 清晰
[ ] 代码提交 + push - 完成
[ ] Day 1 deliverable 标记为完成
```

---

**准备好了吗？** 🚀 明天开始Day 1!

如有问题，现在就提出来。

---

**最后更新**: 2025-12-15
**状态**: 准备就绪
