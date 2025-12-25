# Prompt Enhancement v1.1 - 实现计划

**版本**: 1.1.0
**日期**: 2025-12-15
**总工期**: 7 天 (Day 1-7)
**发布**: v1.1.0 MVP

---

## 总体时间表

```
DAY 1-2: Agent Docs Parser (P0) ────────────┐
DAY 2-3: Context & Generator 升级 (P0)     ├─→ v1.1.0 MVP (Day 3 发布)
DAY 4:   Clarity Scorer (P1)               │
DAY 5:   Clarifier (P1)                    │
DAY 6:   Response Cache (P1)               │
DAY 7:   文档、测试、发布准备              └─→ 完成后续优化
```

---

## 阶段 1：Agent Docs Parser (P0)

### 时间: Day 1-2（预计 7-8 小时）

### 目标

完成 Agent Docs Parser 模块，支持解析结构化和灵活的 AGENTS.md 格式。

### 交付物

```
✓ src/agent_docs_parser.py (260 行)
✓ tests/test_agent_docs_parser.py (220 行)
✓ 代码覆盖率 ≥ 80%
✓ API 文档完整
```

### 详细步骤

#### 步骤 1.1：创建文件结构 (30 分钟)

```bash
# 创建主文件
touch src/agent_docs_parser.py
touch tests/test_agent_docs_parser.py

# 定义导出
# 更新 src/__init__.py 添加: from .agent_docs_parser import AgentDocParser, AgentConfig
```

#### 步骤 1.2：定义数据类 (45 分钟)

在 `src/agent_docs_parser.py` 中实现：

```python
@dataclass
class AgentConfig:
    source_file: str
    format_type: str              # "structured" 或 "flexible"
    raw_content: str

    commands: List[str] = field(default_factory=list)
    guidelines: List[str] = field(default_factory=list)
    boundaries: Dict[str, List] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    testing: Dict[str, str] = field(default_factory=dict)

    sections: Dict[str, str] = field(default_factory=dict)
    code_blocks: List[CodeBlock] = field(default_factory=list)

    last_modified: datetime = field(default_factory=datetime.now)
    parse_errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return bool(self.commands or self.guidelines or self.warnings)

    @classmethod
    def empty(cls) -> "AgentConfig":
        return cls(
            source_file="",
            format_type="",
            raw_content=""
        )


@dataclass
class CodeBlock:
    language: str
    content: str
    line_number: int
```

**验收标准**:
- [ ] 类定义完整
- [ ] 所有字段有默认值
- [ ] 有 `is_valid` 和 `empty()` 方法

#### 步骤 1.3：实现格式检测 (1 小时)

```python
class AgentDocParser:
    def detect_format(self, content: str) -> str:
        """检测是结构化还是灵活格式"""
        # 检查是否有 ## Commands 等明确标题
        structured_markers = [
            "## Commands", "## Code Style",
            "## Boundaries", "## Warnings"
        ]
        return "structured" if any(
            marker in content for marker in structured_markers
        ) else "flexible"
```

**验收标准**:
- [ ] 检测正确率 ≥ 95%
- [ ] 有单元测试

#### 步骤 1.4：实现文件搜索 (1 小时)

```python
def find_config_file(self, project_root: str,
                    force_source: Optional[str] = None) -> Optional[str]:
    """按优先级查找 AGENTS.md"""
    SEARCH_PATHS = [
        "./AGENTS.md",
        "./CLAUDE.md",
        "./.github/copilot-instructions.md",
    ]

    # 实现优先级搜索逻辑
```

**验收标准**:
- [ ] 按正确优先级搜索
- [ ] 多个文件时记录警告
- [ ] force_source 参数工作正常

#### 步骤 1.5：实现结构化解析 (1.5 小时)

```python
def _parse_structured_format(self, content: str) -> AgentConfig:
    """解析 ## Commands, ## Code Style 等明确的结构"""
    # 按 ## 标题分割
    # 对每个 section 识别类型并提取
    # 代码块、列表项等
```

**验收标准**:
- [ ] 正确提取 commands
- [ ] 正确提取 guidelines
- [ ] 正确识别 boundaries
- [ ] 单元测试通过

#### 步骤 1.6：实现灵活格式解析 (1.5 小时)

```python
def _parse_flexible_format(self, content: str) -> AgentConfig:
    """灵活的官方标准格式"""
    # 关键词匹配
    # 文本提取
    # 合理的默认处理
```

**验收标准**:
- [ ] 能识别常见命令
- [ ] 能提取警告信息
- [ ] 容错能力强
- [ ] 单元测试通过

#### 步骤 1.7：编写测试 (2 小时)

创建 `tests/test_agent_docs_parser.py`：

```python
def test_find_config_file():
    """测试文件查找"""

def test_detect_format_structured():
    """测试格式检测 - 结构化"""

def test_detect_format_flexible():
    """测试格式检测 - 灵活"""

def test_parse_structured():
    """测试结构化解析"""

def test_parse_flexible():
    """测试灵活解析"""

def test_extract_commands():
    """测试命令提取"""

def test_extract_warnings():
    """测试警告提取"""

def test_handle_missing_file():
    """测试缺失文件处理"""

def test_empty_file():
    """测试空文件处理"""
```

**验收标准**:
- [ ] 8 个测试都通过
- [ ] 覆盖率 ≥ 80%
- [ ] `pytest tests/test_agent_docs_parser.py -v` 通过

#### 步骤 1.8：文档和注释 (1 小时)

- [ ] 完整的 Docstring (Google 风格)
- [ ] 类和方法注释
- [ ] 参数和返回值文档
- [ ] 使用示例

**验收标准**:
```bash
# 运行文档检查
python -m pydoc src.agent_docs_parser | head -50
```

### 质量检查清单

在进入步骤 2 前完成：

- [ ] `pytest tests/test_agent_docs_parser.py -v` 通过
- [ ] `pytest --cov=src.agent_docs_parser --cov-report=term-missing` ≥ 80%
- [ ] `black src/agent_docs_parser.py` 格式正确
- [ ] `flake8 src/agent_docs_parser.py` 无错误
- [ ] `mypy src/agent_docs_parser.py` 通过
- [ ] 所有 TODO 注释已完成

---

## 阶段 2：Context Collector & Generator 升级 (P0)

### 时间: Day 2-3（预计 5-6 小时）

### 目标

升级现有模块，集成 Agent Docs Parser 输出。

### 交付物

```
✓ src/context_collector.py (升级)
✓ src/enhanced_prompt_generator.py (升级)
✓ 新增字段和输出区块
✓ 端到端集成测试
```

### 详细步骤

#### 步骤 2.1：升级 Context Collector (2 小时)

**修改 `src/context_collector.py`**:

```python
class ContextCollector:
    def collect(self, project_root: str,
               config_file: Optional[str] = None) -> EnhancementContext:
        """收集上下文

        新增字段 (v1.1):
        - agents_config: AgentConfig
        - clarity_score: float
        """

        # 现有逻辑...

        # 新增：解析 AGENTS.md
        parser = AgentDocParser()
        config_file = config_file or parser.find_config_file(project_root)
        agents_config = parser.parse(config_file) if config_file else AgentConfig.empty()

        # 新增：评分
        scorer = ClarityScorer()
        clarity_score = scorer.score(user_prompt)

        # 返回扩展的 context
        return EnhancementContext(
            # 现有字段...
            agents_config=agents_config,
            clarity_score=clarity_score,
            clarity_level=scorer.interpret(clarity_score)["level"]
        )
```

**验收标准**:
- [ ] `agents_config` 字段可用
- [ ] `clarity_score` 字段可用
- [ ] 向后兼容现有代码
- [ ] 集成测试通过

#### 步骤 2.2：升级 Generator (1.5 小时)

**修改 `src/enhanced_prompt_generator.py`**:

在输出中新增 3 个区块：

```python
def generate(self, context: EnhancementContext) -> EnhancedPrompt:
    """生成增强 prompt

    新增区块 (v1.1):
    """

    # 现有逻辑...

    # 新增：项目规范
    project_norms = self._format_norms(context.agents_config)

    # 新增：边界约束
    boundary_constraints = self._format_boundaries(context.agents_config)

    # 新增：特别警告
    special_warnings = self._format_warnings(context.agents_config)

    return EnhancedPrompt(
        # 现有字段...
        project_norms=project_norms,
        boundary_constraints=boundary_constraints,
        special_warnings=special_warnings,
        agents_config_source=context.agents_config.source_file
    )

def _format_norms(self, config: AgentConfig) -> str:
    """格式化项目规范"""
    if not config.guidelines:
        return ""
    return "## 项目规范 [来自 AGENTS.md]\n\n" + \
           "\n".join(f"- {g}" for g in config.guidelines)

def _format_boundaries(self, config: AgentConfig) -> str:
    """格式化边界约束"""
    if not config.boundaries:
        return ""
    lines = ["## 边界约束 ⚠️ [来自 AGENTS.md]\n"]
    for boundary_type, items in config.boundaries.items():
        if items:
            lines.append(f"**{boundary_type}**:")
            for item in items:
                lines.append(f"  - {item}")
    return "\n".join(lines)

def _format_warnings(self, config: AgentConfig) -> str:
    """格式化特别警告"""
    if not config.warnings:
        return ""
    return "## 特别警告 🚨 [来自 AGENTS.md]\n\n" + \
           "\n".join(f"- {w}" for w in config.warnings)
```

**验收标准**:
- [ ] 3 个新方法实现完整
- [ ] 格式化输出美观正确
- [ ] 集成测试通过

#### 步骤 2.3：端到端集成测试 (1.5 小时)

创建或扩展集成测试：

```python
def test_full_enhancement_flow():
    """测试完整的增强流程"""

    # 1. 创建测试项目
    project_root = setup_test_project()

    # 2. 创建 AGENTS.md
    create_agents_md(project_root)

    # 3. 收集上下文
    collector = ContextCollector()
    context = collector.collect(project_root)

    # 验证新字段
    assert context.agents_config is not None
    assert context.clarity_score >= 0.0

    # 4. 生成增强 prompt
    generator = EnhancedPromptGenerator()
    enhanced = generator.generate(context)

    # 验证新区块
    assert "项目规范" in enhanced.project_norms
    assert "边界约束" in enhanced.boundary_constraints
    assert "特别警告" in enhanced.special_warnings

    # 5. 格式化输出
    output = generator.format_output(enhanced)
    assert len(output) > 0
    assert "## 项目规范" in output
```

**验收标准**:
- [ ] 完整流程测试通过
- [ ] 所有新字段都填充
- [ ] 输出格式正确

#### 步骤 2.4：文档更新 (1 小时)

- [ ] 更新 API_V1.1.md 的新字段文档
- [ ] 添加升级指南 (MIGRATION.md)
- [ ] 更新现有函数的 Docstring
- [ ] 更新 README 的使用示例

**验收标准**:
- [ ] 新 API 完整文档化
- [ ] 升级指南清晰
- [ ] 所有示例可运行

### 质量检查清单

- [ ] `pytest tests/ -v --cov=src` 通过，覆盖率 ≥ 80%
- [ ] 所有端到端测试通过
- [ ] 代码格式正确 (black, flake8, mypy)
- [ ] 现有功能未破坏
- [ ] 文档完整

---

## 阶段 3-6：P1 功能（可选，可延后）

### 预计时间表

- **Day 4**: Clarity Scorer (基础版)
- **Day 5**: Clarifier (问询模块)
- **Day 6**: Response Cache (缓存系统)
- **Day 7**: 文档、优化、发布

由于篇幅限制，详细步骤见 DESIGN_V1.1.md 的"实现步骤"章节。

---

## v1.1.0 MVP 发布清单

### Day 3 发布前检查

#### 代码质量

- [ ] `pytest tests/ -v --cov=src` 通过
- [ ] 覆盖率 ≥ 80%
- [ ] `black src/ tests/` 通过
- [ ] `flake8 src/ tests/` 无错误
- [ ] `mypy src/` 通过
- [ ] 所有 TODO 注释已完成

#### 文档完整性

- [ ] DESIGN_V1.1.md 完整
- [ ] API_V1.1.md 完整
- [ ] AGENTS_MD_GUIDE.md 完整
- [ ] IMPLEMENTATION_PLAN.md 完整
- [ ] examples/AGENTS.md.example 完整
- [ ] 所有新 API 都有 docstring

#### 功能验证

- [ ] Agent Docs Parser 解析结构化格式
- [ ] Agent Docs Parser 解析灵活格式
- [ ] Context Collector 集成 AGENTS.md
- [ ] Enhanced Prompt Generator 输出新区块
- [ ] 完整流程能端到端运行
- [ ] 错误处理优雅

#### 兼容性

- [ ] 向后兼容现有 API
- [ ] 现有项目不需要改动
- [ ] 新的 AGENTS.md 是可选的

#### 文件完整性

- [ ] 源文件: agent_docs_parser.py
- [ ] 源文件: models.py (数据类)
- [ ] 测试文件: test_agent_docs_parser.py
- [ ] 文档: 所有 4 个文档文件
- [ ] 示例: AGENTS.md.example
- [ ] README 已更新

### 发布步骤

```bash
# 1. 最后一次完整测试
pytest tests/ -v --cov=src --cov-report=html

# 2. 更新版本信息
# src/__version__ = "1.1.0"
# CHANGELOG.md 更新

# 3. 创建 git 标签
git tag -a v1.1.0 -m "Release v1.1.0 - Agent Docs Parser + AGENTS.md Support"

# 4. 创建 Release Notes
# GitHub Release with CHANGELOG 内容

# 5. 推送
git push origin main
git push origin v1.1.0
```

---

## 常见问题和解决方案

### Q1: 单元测试如何模拟 AGENTS.md 文件？

A: 使用 `tmpdir` 或 `tmp_path` fixture：

```python
def test_parse_real_file(tmp_path):
    # 创建临时文件
    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("## Commands\nnpm test")

    # 测试
    parser = AgentDocParser()
    config = parser.parse(str(agents_file))
    assert config.commands
```

### Q2: 如何处理格式解析失败？

A: 返回 `AgentConfig.empty()`：

```python
def parse(self, file_path: str) -> AgentConfig:
    try:
        # 解析逻辑
        return config
    except Exception as e:
        logger.error(f"Parse failed: {e}")
        return AgentConfig.empty()
```

### Q3: 向后兼容性如何保证？

A: 新字段都有默认值，现有函数不修改签名：

```python
# ✅ 好 - 新参数有默认值
def collect(self, project_root: str,
           config_file: Optional[str] = None) -> EnhancementContext:
    # 现有代码可以继续工作

# ❌ 不好 - 修改现有参数
def collect(self, project_root: str, must_have_agents: bool) -> ...:
    # 会破坏现有代码
```

### Q4: 如何测试性能？

A: 添加性能测试：

```python
def test_parsing_performance(benchmark):
    """测试解析性能"""
    parser = AgentDocParser()

    def parse():
        return parser.parse_from_content(large_agents_md)

    result = benchmark(parse)
    # benchmark 会自动测量和报告时间
```

---

## 风险和缓解措施

| 风险 | 影响 | 缓解 |
|------|------|------|
| 格式解析失败 | 流程中断 | 容错处理，返回空config |
| 文件不存在 | 跳过 AGENTS.md | 使用 find_config_file，允许不存在 |
| 格式检测错误 | 解析错误 | 启发式规则 + 单元测试覆盖 |
| 性能下降 | 响应变慢 | 缓存优化，profile 检查 |

---

## 成功标准

### v1.1.0 MVP 成功标准

✅ **功能完整性**
- Agent Docs Parser 支持双格式
- Context Collector 集成 AGENTS.md
- Enhanced Prompt Generator 输出新区块

✅ **代码质量**
- 测试覆盖率 ≥ 80%
- 所有测试通过
- 代码符合风格标准

✅ **文档完整性**
- 4 个设计/API 文档完整
- 示例代码可运行
- 升级指南清晰

✅ **用户体验**
- API 易用
- 错误信息清晰
- 优雅处理边界情况

---

## 后续计划

### v1.2.0 (Day 4-6)

- Clarifier: 交互式问询
- Response Cache: 缓存优化
- Clarity Scorer: 高级版

### v1.3.0 (Day 9-10)

- 向量相似度计算
- ML 模型优化
- 性能优化

---

**文档完成时间**: 2025-12-15
**计划版本**: 1.0
**下一步**: 开始 Day 1 实现

