# Prompt Enhancement v1.1 - 完整设计文档

**版本**: 1.1.0
**日期**: 2025-12-15
**作者**: Jodykwong
**状态**: 设计阶段

---

## 目录

1. [总体架构](#总体架构)
2. [模块设计](#模块设计)
3. [数据结构](#数据结构)
4. [API 接口定义](#api-接口定义)
5. [实现步骤](#实现步骤)
6. [文件清单](#文件清单)
7. [测试策略](#测试策略)
8. [性能要求](#性能要求)

---

## 总体架构

### 系统设计总览

```
┌─────────────────────────────────────────────────────────────────┐
│                    现有架构 (v1.01)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   tech_stack_detector → project_structure_analyzer              │
│           ↓                       ↓                               │
│   git_history_analyzer → context_collector                       │
│                              ↓                                    │
│                    enhanced_prompt_generator                      │
│                              ↓                                    │
│                      DeepSeek API 增强                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    升级架构 (v1.1)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              输入处理 (新增)                               │   │
│  │                                                            │   │
│  │  Agent Docs Parser ← 结构化 + 灵活双格式支持              │   │
│  │  Clarity Scorer    ← 意图明确度评分                       │   │
│  │  Clarifier         ← 交互问询 (P1)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│             ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Context Collector (升级)                        │   │
│  │                                                            │   │
│  │   现有输入:                    新增输入:                    │   │
│  │   • tech_stack_detector       • agents_config              │   │
│  │   • project_structure         • clarity_score              │   │
│  │   • git_history               • user_preferences           │   │
│  └──────────────────────────────────────────────────────────┘   │
│             ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │      Enhanced Prompt Generator (升级)                      │   │
│  │                                                            │   │
│  │   新增输出区块:                                             │   │
│  │   • 项目规范 [来自 AGENTS.md]                              │   │
│  │   • 边界约束 ⚠️  [来自 AGENTS.md]                          │   │
│  │   • 特别警告 🚨 [来自 AGENTS.md]                           │   │
│  │   • 澄清的任务 [来自 Clarifier]                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│             ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        Response Cache (P1，可选)                           │   │
│  │                                                            │   │
│  │   缓存优化：                                                │   │
│  │   • 项目上下文 (5 分钟)                                     │   │
│  │   • AGENTS.md 配置 (文件变更监控)                          │   │
│  │   • 相似 Prompt (向量相似度)                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│             ↓                                                     │
│   DeepSeek API 增强 / 输出到用户                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 关键设计原则

1. **渐进式迭代** - v1.1.0 (核心) + v1.2.0 (P1功能)
2. **双格式兼容** - 结构化格式 + 灵活格式同时支持
3. **向后兼容** - 现有模块升级不破坏 API
4. **容错能力** - 缺失配置时优雅降级
5. **性能驱动** - 缓存和预处理优化响应速度

---

## 模块设计

### 模块 A：Agent Docs Parser (核心)

**文件**: `agent_docs_parser.py`
**职责**: 解析项目中的 AGENTS.md，支持结构化和灵活格式

#### A.1 功能概述

```
输入：
  - 文件路径：./AGENTS.md (或其他搜索路径)
  - 格式检测：自动识别结构化 vs 灵活格式

输出：
  - 统一的内部数据结构 (AgentConfig)
  - 包含：commands, guidelines, boundaries, warnings 等

支持的格式：
  1. 结构化格式 (推荐)：明确的 Markdown sections
     ## Commands
     ## Code Style
     ## Boundaries
     ## Warnings

  2. 灵活格式 (官方标准)：自由 Markdown + 关键词提取
```

#### A.2 搜索优先级

```yaml
搜索顺序:
  1. ./AGENTS.md              (项目级别，最高优先)
  2. ./CLAUDE.md              (Claude Code 标准)
  3. ./.github/copilot-instructions.md
  4. ./.github/agents/*.md    (GitHub agents)
  5. ./.bmad/**/*.md          (BMAD 方法文件)

搜索策略:
  - 按优先级查找
  - 使用第一个找到的文件
  - 多个文件时记录警告日志
  - 提供 --config-source 参数让用户显式指定
```

#### A.3 数据结构

```python
@dataclass
class AgentConfig:
    """
    AGENTS.md 解析结果的统一表示
    """
    # 源信息
    source_file: str              # 源文件路径
    format_type: str              # "structured" 或 "flexible"
    raw_content: str              # 原始文件内容

    # 抽取的内容
    commands: List[str]           # 识别的命令列表
    guidelines: List[str]         # 代码规范和最佳实践
    boundaries: Dict[str, List]   # 边界约束
    warnings: List[str]           # 警告信息
    testing: Dict[str, str]       # 测试相关配置

    # 段落组织
    sections: Dict[str, str]      # 按标题组织的原始内容
    code_blocks: List[CodeBlock]  # 所有代码块

    # 元数据
    last_modified: datetime       # 文件最后修改时间
    parse_errors: List[str]       # 解析过程中的错误

    @property
    def is_valid(self) -> bool:
        """检查是否有有效的内容"""
        return bool(
            self.commands or
            self.guidelines or
            self.boundaries or
            self.warnings
        )


@dataclass
class CodeBlock:
    """代码块"""
    language: str                 # bash, python, js 等
    content: str                  # 代码内容
    line_number: int              # 在源文件中的行号
```

#### A.4 实现算法

**算法 1：格式检测**
```python
def detect_format(content: str) -> str:
    """
    自动检测格式类型
    返回: "structured" 或 "flexible"

    启发式规则：
    1. 如果包含 "## Commands" 等明确的结构化标题 → structured
    2. 如果有明确的 YAML 前置 (---)            → structured
    3. 否则                                   → flexible
    """
```

**算法 2：结构化格式解析**
```python
def parse_structured_format(content: str) -> AgentConfig:
    """
    解析结构化格式（明确的 Markdown sections）

    步骤：
    1. 按 ## 标题分割内容
    2. 对每个 section:
       - 识别 section 类型 (commands/guidelines/boundaries/warnings)
       - 提取内容（代码块/列表/文本）
    3. 返回 AgentConfig
    """
```

**算法 3：灵活格式解析**
```python
def parse_flexible_format(content: str) -> AgentConfig:
    """
    解析灵活格式（官方 agents.md 标准）

    步骤：
    1. 按 # 标题分割为 sections
    2. 提取所有代码块
    3. 关键词匹配：
       - commands: 识别 npm/bash/python/go 等命令
       - guidelines: 粗体文本/列表项
       - warnings: 包含 warning/caution/never/avoid 的段落
       - testing: 包含 test/validation 的段落
    4. 返回 AgentConfig
    """
```

#### A.5 伪代码实现

```python
class AgentDocParser:
    """官方标准 agents.md 解析器"""

    # 搜索路径
    SEARCH_PATHS = [
        "./AGENTS.md",
        "./CLAUDE.md",
        "./.github/copilot-instructions.md",
    ]

    # 关键词映射
    SECTION_KEYWORDS = {
        "commands": ["command", "setup", "installation", "run", "bash"],
        "guidelines": ["code style", "convention", "guideline", "best practice"],
        "boundaries": ["never", "avoid", "don't", "boundary", "constraint"],
        "warnings": ["warning", "caution", "important", "deprecated"],
        "testing": ["test", "testing", "validation", "qa"],
    }

    def find_config_file(self, project_root: str,
                        force_source: str = None) -> Optional[str]:
        """
        查找配置文件

        Args:
            project_root: 项目根目录
            force_source: 指定的配置文件名

        Returns:
            找到的文件路径或 None
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
        解析 AGENTS.md 文件

        Args:
            file_path: 文件路径

        Returns:
            AgentConfig 对象
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

            return config

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return AgentConfig.empty()

    def detect_format(self, content: str) -> str:
        """检测格式类型"""
        # 检查结构化标题
        structured_markers = [
            "## Commands", "## Code Style",
            "## Boundaries", "## Warnings"
        ]
        if any(marker in content for marker in structured_markers):
            return "structured"
        return "flexible"

    def _parse_structured_format(self, content: str) -> AgentConfig:
        """解析结构化格式"""
        config = AgentConfig()

        # 按 ## 分割
        sections = self._split_by_heading(content, level=2)

        for section_name, section_content in sections.items():
            if "command" in section_name.lower():
                config.commands = self._extract_commands(section_content)
            elif "style" in section_name.lower():
                config.guidelines = self._extract_guidelines(section_content)
            elif "boundar" in section_name.lower():
                config.boundaries = self._extract_boundaries(section_content)
            elif "warning" in section_name.lower():
                config.warnings = self._extract_warnings(section_content)
            elif "test" in section_name.lower():
                config.testing = self._extract_testing(section_content)

            config.sections[section_name] = section_content

        return config

    def _parse_flexible_format(self, content: str) -> AgentConfig:
        """解析灵活格式"""
        config = AgentConfig()

        # 提取所有代码块
        config.code_blocks = self._extract_all_code_blocks(content)

        # 按内容推断
        config.commands = self._infer_commands(content, config.code_blocks)
        config.guidelines = self._infer_guidelines(content)
        config.boundaries = self._infer_boundaries(content)
        config.warnings = self._infer_warnings(content)
        config.testing = self._infer_testing(content)

        # 按 # 分割为 sections
        config.sections = self._split_by_heading(content, level=1)

        return config

    def _extract_commands(self, section: str) -> List[str]:
        """从 section 中提取命令"""
        commands = []

        # 从代码块提取
        code_blocks = re.findall(
            r'```(?:bash|shell|sh)?\n(.*?)\n```',
            section,
            re.DOTALL
        )

        for block in code_blocks:
            for line in block.split('\n'):
                line = line.strip()
                # 识别常见命令模式
                if any(line.startswith(cmd) for cmd in
                       ['npm ', 'yarn ', 'pip ', 'python ', 'pytest ']):
                    commands.append(line)

        return commands

    def _extract_guidelines(self, section: str) -> List[str]:
        """提取代码规范"""
        guidelines = []

        # 提取列表项
        bullets = re.findall(r'^[\s]*[-*+]\s+(.+?)$', section, re.MULTILINE)
        guidelines.extend(bullets)

        # 提取粗体文本
        bold = re.findall(r'\*\*(.+?)\*\*', section)
        guidelines.extend(bold)

        return guidelines

    def _extract_warnings(self, section: str) -> List[str]:
        """提取警告"""
        warnings = []

        # 按段落分析
        paragraphs = section.split('\n\n')
        for para in paragraphs:
            if any(kw in para.lower() for kw in
                   ['warning', 'caution', 'important']):
                warnings.append(para.strip())

        return warnings

    def _extract_boundaries(self, section: str) -> Dict[str, List]:
        """提取边界约束"""
        boundaries = {
            "never_modify": [],
            "require_approval": [],
            "deprecated": []
        }

        # 提取列表项并分类
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
        """提取测试配置"""
        testing = {}

        # 提取命令
        commands = self._extract_commands(section)
        if commands:
            testing["commands"] = commands

        # 提取覆盖率等配置
        if "coverage" in section.lower():
            match = re.search(r'coverage.*?(\d+)%', section, re.IGNORECASE)
            if match:
                testing["coverage_threshold"] = match.group(1)

        return testing

    def _infer_commands(self, content: str,
                       code_blocks: List[CodeBlock]) -> List[str]:
        """从灵活格式推断命令"""
        commands = []

        for block in code_blocks:
            if block.language in ['bash', 'shell', 'sh']:
                for line in block.content.split('\n'):
                    line = line.strip()
                    if any(line.startswith(cmd) for cmd in
                           ['npm ', 'yarn ', 'pip ', 'python ']):
                        commands.append(line)

        return commands

    def _infer_guidelines(self, content: str) -> List[str]:
        """从灵活格式推断规范"""
        guidelines = []

        # 提取所有列表项
        bullets = re.findall(r'^[\s]*[-*+]\s+(.+?)$', content, re.MULTILINE)
        guidelines.extend(bullets)

        # 提取粗体和斜体
        emphasized = re.findall(r'\*\*(.+?)\*\*|_(.+?)_', content)
        for group in emphasized:
            guidelines.extend([item for item in group if item])

        return guidelines

    def _infer_warnings(self, content: str) -> List[str]:
        """从灵活格式推断警告"""
        warnings = []

        warning_keywords = ['warning', 'caution', 'never', 'avoid',
                           'deprecated', '⚠️', '🚨']

        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if any(kw.lower() in para.lower() for kw in warning_keywords):
                warnings.append(para.strip())

        return warnings

    def _infer_boundaries(self, content: str) -> Dict[str, List]:
        """从灵活格式推断边界约束"""
        boundaries = {"never_modify": [], "require_approval": []}

        lines = content.split('\n')
        for line in lines:
            if "never" in line.lower() or "don't" in line.lower():
                boundaries["never_modify"].append(line.strip())
            elif "approval" in line.lower():
                boundaries["require_approval"].append(line.strip())

        return boundaries

    def _infer_testing(self, content: str) -> Dict[str, str]:
        """从灵活格式推断测试配置"""
        testing = {}

        # 查找框架
        frameworks = ["pytest", "unittest", "jest", "mocha"]
        for fw in frameworks:
            if fw in content.lower():
                testing["framework"] = fw
                break

        # 查找覆盖率
        match = re.search(r'coverage.*?(\d+)%', content, re.IGNORECASE)
        if match:
            testing["coverage_threshold"] = match.group(1)

        return testing

    def _extract_all_code_blocks(self, content: str) -> List[CodeBlock]:
        """提取所有代码块"""
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

    def _split_by_heading(self, content: str,
                         level: int = 2) -> Dict[str, str]:
        """按标题级别分割内容"""
        sections = {}
        heading_pattern = f"^{'#' * level} "

        current_section = None
        current_content = []

        for line in content.split('\n'):
            if re.match(heading_pattern, line):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


# 使用示例
if __name__ == "__main__":
    parser = AgentDocParser()

    # 查找 AGENTS.md
    config_file = parser.find_config_file(".")

    if config_file:
        # 解析
        config = parser.parse(config_file)

        # 输出结果
        print(f"Source: {config.source_file}")
        print(f"Format: {config.format_type}")
        print(f"Commands: {config.commands}")
        print(f"Guidelines: {config.guidelines}")
        print(f"Warnings: {config.warnings}")
        print(f"Boundaries: {config.boundaries}")
```

---

### 模块 B：Clarity Scorer (P0)

**文件**: `clarity_scorer.py`
**职责**: 评估用户 prompt 的意图明确度

#### B.1 评分规则

```python
def calculate_clarity_score(prompt: str, context: dict) -> float:
    """
    计算 prompt 的明确度评分 (0-1)

    评分规则：
    """
    score = 0.0

    # 1. 包含具体文件名 (+0.25)
    if _contains_filename(prompt, context.get("project_files", [])):
        score += 0.25

    # 2. 包含具体函数/类名 (+0.2)
    if _contains_symbol(prompt, context.get("symbols", [])):
        score += 0.2

    # 3. 包含明确动作动词 (+0.2)
    action_verbs = [
        "添加", "删除", "修复", "重构", "优化", "测试",
        "add", "remove", "fix", "refactor", "optimize", "test"
    ]
    if any(verb in prompt.lower() for verb in action_verbs):
        score += 0.2

    # 4. 包含技术细节 (+0.2)
    if _contains_technical_terms(prompt):
        score += 0.2

    # 5. 任务范围明确 (+0.15)
    if _scope_is_clear(prompt):
        score += 0.15

    return min(score, 1.0)
```

#### B.2 触发策略

| 分数 | 判定 | 动作 |
|------|------|------|
| 0.6 - 1.0 | 明确 | 直接增强，无需问询 |
| 0.3 - 0.6 | 一般 | 增强 + 可选问询 |
| 0.0 - 0.3 | 模糊 | 强制问询或提示 |

#### B.3 实现代码框架

```python
class ClarityScorer:
    """prompt 意图明确度评分器"""

    ACTION_VERBS = {
        "zh": ["添加", "删除", "修复", "重构", "优化", "测试",
               "创建", "更新", "改进"],
        "en": ["add", "remove", "fix", "refactor", "optimize",
               "test", "create", "update", "improve"]
    }

    TECHNICAL_TERMS = [
        "api", "database", "authentication", "caching", "deployment",
        "performance", "security", "testing", "integration",
        # 中文
        "接口", "数据库", "认证", "缓存", "部署",
        "性能", "安全", "测试", "集成"
    ]

    def __init__(self, context: dict = None):
        self.context = context or {}

    def score(self, prompt: str) -> float:
        """计算明确度评分"""
        score = 0.0

        # 1. 文件名 (+0.25)
        if self._has_filename(prompt):
            score += 0.25

        # 2. 函数/类名 (+0.2)
        if self._has_symbol(prompt):
            score += 0.2

        # 3. 动作动词 (+0.2)
        if self._has_action_verb(prompt):
            score += 0.2

        # 4. 技术细节 (+0.2)
        if self._has_technical_terms(prompt):
            score += 0.2

        # 5. 范围明确 (+0.15)
        if self._has_clear_scope(prompt):
            score += 0.15

        return min(score, 1.0)

    def _has_filename(self, prompt: str) -> bool:
        """检查是否包含文件名"""
        # 检查常见文件扩展名
        patterns = [
            r'\w+\.(py|js|ts|java|cpp|go|rs)',
            r'\.\/[\w/]+',
            r'src\/[\w\/]+',
        ]
        return any(re.search(p, prompt) for p in patterns)

    def _has_symbol(self, prompt: str) -> bool:
        """检查是否包含符号（函数/类名）"""
        # 检查 PascalCase 或 snake_case
        patterns = [
            r'[A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*',  # PascalCase
            r'\b[a-z]+(?:_[a-z]+)+\(',  # snake_case 函数
        ]
        return any(re.search(p, prompt) for p in patterns)

    def _has_action_verb(self, prompt: str) -> bool:
        """检查是否包含动作动词"""
        all_verbs = self.ACTION_VERBS["zh"] + self.ACTION_VERBS["en"]
        return any(verb in prompt.lower() for verb in all_verbs)

    def _has_technical_terms(self, prompt: str) -> bool:
        """检查是否包含技术术语"""
        return any(term in prompt.lower() for term in self.TECHNICAL_TERMS)

    def _has_clear_scope(self, prompt: str) -> bool:
        """检查范围是否明确"""
        # 包含数字、范围词、具体描述
        scope_indicators = [
            r'\b(all|entire|full|complete)\b',
            r'\b(single|one|specific)\b',
            r'for .* (purpose|reason|goal)',
            r'\b(before|after|when|while)\b',
        ]
        return any(re.search(p, prompt, re.I) for p in scope_indicators)

    def interpret(self, score: float) -> dict:
        """解释评分"""
        if score >= 0.6:
            return {
                "level": "明确",
                "action": "direct_enhance",
                "need_clarify": False
            }
        elif score >= 0.3:
            return {
                "level": "一般",
                "action": "enhance_with_optional_clarify",
                "need_clarify": False
            }
        else:
            return {
                "level": "模糊",
                "action": "force_clarify",
                "need_clarify": True
            }
```

---

### 模块 C：Clarifier (P1，可选)

**文件**: `clarifier.py`
**职责**: 当任务意图模糊时，通过问询收集关键信息

#### C.1 问询模板系统

```yaml
目录结构:
  skill_templates/clarifier/
  ├── authentication.yaml
  ├── testing.yaml
  ├── refactoring.yaml
  ├── security.yaml
  ├── api.yaml
  ├── database.yaml
  ├── performance.yaml
  └── general.yaml

模板格式:
  name: "认证与授权"
  trigger_keywords: ["认证", "登录", "auth"]
  questions:
    - id: "auth_method"
      text: "选择认证方式"
      type: "single_choice"
      options:
        - label: "JWT Token"
          value: "jwt"
        - label: "Session"
          value: "session"
```

#### C.2 交互流程

```
1. Clarity Scorer 得分 < 0.3
   ↓
2. 触发 Clarifier
   ↓
3. 关键词匹配 → 选择模板
   ↓
4. 显示问题列表
   ↓
5. 用户输入答案
   ↓
6. 合并回 prompt
   ↓
7. 再次计分（可选）
```

---

### 模块 D：Response Cache (P1，可选)

**文件**: `response_cache.py`
**职责**: 缓存增强结果，加快响应

#### D.1 缓存策略

| 类型 | 缓存时间 | 说明 |
|------|---------|------|
| 项目上下文 | 5 分钟 | context_collector 结果 |
| AGENTS.md | 文件变更 | 文件不变则不重新解析 |
| Prompt 相似 | 1 小时 | 相似度 > 0.85 的 prompt |

#### D.2 存储位置

```
.pe-cache/
├── context_cache.json      # 项目上下文缓存
├── agents_config.json      # AGENTS.md 解析缓存
├── prompt_cache.json       # Prompt 增强缓存
└── stats.json              # 缓存统计
```

---

## 数据结构

### D.1 统一上下文结构

```python
@dataclass
class EnhancementContext:
    """
    完整的增强上下文
    """
    # 原始输入
    user_prompt: str

    # Agent 配置
    agents_config: AgentConfig

    # 意图评估
    clarity_score: float
    clarity_level: str  # "clear" / "medium" / "unclear"

    # 澄清结果
    clarified_prompt: Optional[str] = None
    clarification_answers: Optional[dict] = None

    # 项目上下文（原有）
    tech_stack: dict
    project_structure: dict
    git_history: dict

    # 源文件信息
    relevant_files: List[str]
    code_snippets: dict

    # 缓存信息
    cache_hit: bool = False
    cache_age_seconds: Optional[int] = None


@dataclass
class EnhancedPrompt:
    """增强后的 prompt"""

    # 原始信息
    original_prompt: str
    clarity_score: float

    # 新增区块（v1.1）
    project_norms: str              # 来自 AGENTS.md
    boundary_constraints: str       # ⚠️
    special_warnings: str           # 🚨

    # 澄清结果
    clarified_task: Optional[str] = None

    # 现有区块
    project_context: str
    relevant_files: str
    code_snippets: str
    best_practices: str

    # 元数据
    generation_time_ms: float
    cache_hit: bool
    agents_config_source: str
```

---

## API 接口定义

### API.1 Agent Docs Parser

```python
class AgentDocParser:

    def find_config_file(
        self,
        project_root: str,
        force_source: Optional[str] = None
    ) -> Optional[str]:
        """
        查找 AGENTS.md 文件

        Args:
            project_root: 项目根目录
            force_source: 强制指定的源文件

        Returns:
            找到的文件路径或 None

        Raises:
            FileNotFoundError: 如果强制指定的文件不存在
        """

    def parse(self, file_path: str) -> AgentConfig:
        """
        解析 AGENTS.md 文件

        Args:
            file_path: 文件路径

        Returns:
            AgentConfig 对象
        """

    def parse_from_content(
        self,
        content: str,
        source_name: str = "inline"
    ) -> AgentConfig:
        """从内容直接解析"""

    def detect_format(self, content: str) -> str:
        """检测格式类型"""

    def get_commands(self, config: AgentConfig) -> List[str]:
        """获取命令列表"""

    def get_guidelines(self, config: AgentConfig) -> List[str]:
        """获取代码规范"""

    def get_warnings(self, config: AgentConfig) -> List[str]:
        """获取警告信息"""

    def get_boundaries(self, config: AgentConfig) -> Dict:
        """获取边界约束"""
```

### API.2 Context Collector (升级)

```python
class ContextCollector:

    def collect(
        self,
        project_root: str,
        config_file: Optional[str] = None
    ) -> EnhancementContext:
        """
        收集完整上下文

        Changes in v1.1:
        - 新增 agents_config 字段
        - 新增 clarity_score 字段

        Args:
            project_root: 项目根目录
            config_file: AGENTS.md 文件路径（可选）

        Returns:
            EnhancementContext 对象
        """
```

### API.3 Enhanced Prompt Generator (升级)

```python
class EnhancedPromptGenerator:

    def generate(
        self,
        context: EnhancementContext
    ) -> EnhancedPrompt:
        """
        生成增强 prompt

        Changes in v1.1:
        - 新增 project_norms 区块
        - 新增 boundary_constraints 区块
        - 新增 special_warnings 区块
        - 新增 clarified_task 区块

        Args:
            context: 增强上下文

        Returns:
            EnhancedPrompt 对象
        """

    def format_output(
        self,
        prompt: EnhancedPrompt,
        format: str = "markdown"
    ) -> str:
        """
        格式化输出

        Args:
            prompt: 增强 prompt
            format: 输出格式 (markdown / plain)

        Returns:
            格式化的字符串
        """
```

### API.4 Clarity Scorer

```python
class ClarityScorer:

    def score(self, prompt: str) -> float:
        """
        评分 prompt

        Args:
            prompt: 用户输入的 prompt

        Returns:
            0-1 之间的评分
        """

    def interpret(self, score: float) -> dict:
        """
        解释评分

        Returns:
            {
                "level": "clear" / "medium" / "unclear",
                "action": "direct_enhance" / "clarify",
                "need_clarify": bool
            }
        """
```

---

## 实现步骤

### 阶段 1：Agent Docs Parser (P0)

**目标**: Day 1-2 完成
**交付物**: `agent_docs_parser.py` + 单元测试

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 1.1 | 创建文件结构 | 30m | 文件存在 |
| 1.2 | 定义数据结构 | 45m | @dataclass 定义完整 |
| 1.3 | 实现格式检测 | 1h | 测试通过 |
| 1.4 | 实现结构化解析 | 1.5h | 5 个测试通过 |
| 1.5 | 实现灵活格式解析 | 1.5h | 5 个测试通过 |
| 1.6 | 编写单元测试 | 2h | 8 个测试，覆盖率 > 80% |
| 1.7 | 文档和注释 | 1h | Docstring 完整 |

### 阶段 2：Context Collector & Generator 升级 (P0)

**目标**: Day 2-3 完成
**交付物**: 升级后的 context_collector.py 和 enhanced_prompt_generator.py

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 2.1 | 升级 Context Collector | 2h | agents_config 字段可用 |
| 2.2 | 升级 Prompt Generator | 1.5h | 新增 3 个输出区块 |
| 2.3 | 集成测试 | 1.5h | 端到端测试通过 |
| 2.4 | 文档更新 | 1h | API 文档更新 |

### 阶段 3：Clarity Scorer (P1)

**目标**: Day 4 完成
**交付物**: `clarity_scorer.py` + 测试

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 3.1 | 实现评分逻辑 | 1.5h | 5 个特征实现 |
| 3.2 | 编写测试 | 1h | 6 个测试通过 |
| 3.3 | 集成到 Context Collector | 1h | 字段可用 |

### 阶段 4：Clarifier (P1)

**目标**: Day 5 完成
**交付物**: `clarifier.py` + 模板

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 4.1 | 创建问询模板 | 2h | 7 个 YAML 模板 |
| 4.2 | 实现 CLI 交互 | 2h | 问询流程可用 |
| 4.3 | 编写测试 | 1h | 5 个测试通过 |

### 阶段 5：Response Cache (P1)

**目标**: Day 6 完成
**交付物**: `response_cache.py`

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 5.1 | 实现缓存逻辑 | 1.5h | 3 种缓存类型 |
| 5.2 | 文件监控 | 1h | AGENTS.md 监控工作 |
| 5.3 | 编写测试 | 1h | 4 个测试通过 |

### 阶段 6：发布准备

**目标**: Day 7 完成
**交付物**: v1.1.0 版本

| 步骤 | 任务 | 时间 | 验收 |
|------|------|------|------|
| 6.1 | 文档更新 | 1.5h | README + API 文档 |
| 6.2 | AGENTS.md 模板 | 1h | 示例文件存在 |
| 6.3 | CHANGELOG 更新 | 1h | v1.1.0 日志完整 |
| 6.4 | 发布 | 0.5h | GitHub Release |

---

## 文件清单

### 新增文件

```
src/
├── agent_docs_parser.py          # Agent Docs Parser (260 行)
├── clarity_scorer.py              # Clarity Scorer (180 行)
├── clarifier.py                   # Clarifier (250 行)
├── response_cache.py              # Response Cache (200 行)
└── models.py                      # 数据类定义 (100 行)

tests/
├── test_agent_docs_parser.py      # (220 行)
├── test_clarity_scorer.py         # (150 行)
├── test_clarifier.py              # (180 行)
└── test_response_cache.py         # (140 行)

skill_templates/clarifier/
├── authentication.yaml
├── testing.yaml
├── refactoring.yaml
├── security.yaml
├── api.yaml
├── database.yaml
├── performance.yaml
└── general.yaml

docs/
├── DESIGN_V1.1.md                 # 本设计文档
├── AGENTS_MD_GUIDE.md             # AGENTS.md 使用指南
└── API_V1.1.md                    # API 文档更新

examples/
└── AGENTS.md.example              # 示例 AGENTS.md
```

### 修改文件

```
src/
├── context_collector.py           # 集成 Agent Docs Parser
├── enhanced_prompt_generator.py   # 新增输出区块
├── __init__.py                    # 导出新模块

.claude/
└── commands/pe.md                 # 支持新参数

README.md                           # 更新用法说明
CHANGELOG.md                        # v1.1.0 变更日志
requirements.txt                    # 新增依赖（如有）
```

---

## 测试策略

### T.1 单元测试

#### Agent Docs Parser 测试

```python
def test_parse_structured_agents_md():
    """测试结构化格式解析"""
    # 输入：带有 ## Commands, ## Code Style 的 AGENTS.md
    # 输出：正确的 AgentConfig
    # 验证：commands, guidelines, boundaries 都被提取

def test_parse_flexible_agents_md():
    """测试灵活格式解析"""
    # 输入：自由格式的 AGENTS.md
    # 输出：通过关键词提取的 AgentConfig
    # 验证：commands 和 warnings 被识别

def test_detect_format():
    """测试格式检测"""
    assert detect_format(structured_content) == "structured"
    assert detect_format(flexible_content) == "flexible"

def test_extract_bash_commands():
    """测试 bash 命令提取"""
    # 从代码块中提取 npm/bash 命令

def test_extract_warnings():
    """测试警告提取"""
    # 识别 "never", "deprecated" 等关键词

def test_handle_missing_file():
    """测试缺失文件处理"""
    # 返回 empty AgentConfig 或 None
```

#### Clarity Scorer 测试

```python
def test_clear_prompt():
    """测试明确 prompt"""
    score = scorer.score("为 src/auth/login.py 添加 JWT 认证")
    assert score >= 0.6

def test_unclear_prompt():
    """测试模糊 prompt"""
    score = scorer.score("改进安全性")
    assert score <= 0.3

def test_medium_prompt():
    """测试中等明确性 prompt"""
    score = scorer.score("添加用户登录功能")
    assert 0.3 <= score < 0.6
```

#### Clarifier 测试

```python
def test_template_matching():
    """测试模板匹配"""
    template = clarifier.find_template("添加认证")
    assert template == "authentication"

def test_question_flow():
    """测试问询流程"""
    # 模拟用户输入
    answers = {"auth_method": "jwt", "mfa": "yes"}
    result = clarifier.clarify(prompt, answers)
    # 验证返回的澄清后的 prompt
```

### T.2 集成测试

```python
def test_end_to_end_enhancement():
    """测试完整增强流程"""
    # 1. 解析 AGENTS.md
    # 2. 评分 prompt
    # 3. 如果需要澄清，执行澄清
    # 4. 生成增强 prompt
    # 验证：最终 prompt 包含所有必要信息
```

### T.3 性能测试

```python
def test_parsing_performance():
    """测试解析性能"""
    # AGENTS.md 解析 < 100ms
    assert parse_time < 0.1

def test_scoring_performance():
    """测试评分性能"""
    # Clarity Scorer < 50ms
    assert score_time < 0.05

def test_cache_hit_performance():
    """测试缓存命中性能"""
    # 缓存命中 < 5ms
    assert cache_hit_time < 0.005
```

### T.4 测试覆盖率要求

| 模块 | 覆盖率目标 |
|------|----------|
| agent_docs_parser.py | 85% |
| clarity_scorer.py | 80% |
| clarifier.py | 75% |
| response_cache.py | 80% |
| **总体** | **80%** |

---

## 性能要求

### P.1 响应时间

| 场景 | 当前 | 目标 v1.1 |
|------|------|----------|
| 冷启动 | 30-60s | 15-20s |
| 缓存命中 | N/A | 2-5s |
| AGENTS.md 解析 | N/A | <100ms |
| Clarity Scorer | N/A | <50ms |

### P.2 内存使用

| 组件 | 内存限制 |
|------|---------|
| 缓存大小 | < 50MB |
| 单个 context | < 10MB |
| 全体进程 | < 200MB |

### P.3 文件 I/O

| 操作 | 目标 |
|------|------|
| AGENTS.md 读取 | <50ms |
| 项目扫描 | <500ms |
| 缓存读写 | <20ms |

---

## 依赖管理

### 新增依赖

```python
# requirements.txt
PyYAML>=6.0          # YAML 解析
pydantic>=2.0        # 数据验证
python-dotenv>=1.0   # 环境变量
```

### 可选依赖

```python
# 用于 Response Cache 向量相似度计算 (v1.2)
sentence-transformers>=2.2.0
numpy>=1.24.0
```

---

## 版本发布计划

### v1.1.0 (MVP) - Day 3

**功能:**
- Agent Docs Parser (双格式支持)
- Context Collector 升级
- Enhanced Prompt Generator 升级 (3 个新区块)
- Clarity Scorer (基础版)

**发布内容:**
- 源代码 + 单元测试
- API 文档
- AGENTS.md 示例和指南
- CHANGELOG

### v1.2.0 (增强) - Day 6

**功能:**
- Clarifier (完整交互问询)
- Response Cache (完整缓存系统)
- Clarity Scorer 高级版

### v1.3.0 (企业版) - Day 10

**功能:**
- 向量相似度计算
- 机器学习 Clarity Scorer
- 性能优化

---

## 附录：AGENTS.md 示例

见文件: `examples/AGENTS.md.example`

```markdown
# Prompt Enhancement Development Guidelines

## Setup

\`\`\`bash
pip install -r requirements.txt
pytest tests/ -v
\`\`\`

## Development Commands

\`\`\`bash
# Run tests
pytest tests/ -v --cov=src

# Run the tool
python main.py --prompt "your prompt"
\`\`\`

## Code Style

- Type hints required for all functions
- snake_case for variables and functions
- PascalCase for classes
- 88 character line length (Black)

## Testing Requirements

- Minimum 80% code coverage
- All tests must pass before merge
- Use pytest fixtures for test data

## Important Warnings

⚠️ Never modify files in the `legacy/` directory without approval

🚨 Deprecated: `old_api()` → use `new_api()` instead

## Boundaries

- Critical path files require code review
- Database migrations need explicit approval
- Security changes must follow OWASP guidelines
```

---

## 结束语

本设计文档定义了 Prompt Enhancement v1.1 的完整实现方案，包括：

✅ 模块设计和算法
✅ API 接口定义
✅ 实现步骤和时间表
✅ 测试策略
✅ 性能要求

**下一步**: 按阶段执行实现步骤，每个阶段完成后进行代码审查和测试。

---

**文档版本**: 1.0
**最后更新**: 2025-12-15
**状态**: 就绪执行
