# Prompt Enhancement v1.3 SOP

> 整合 Anthropic 官方最佳实践的完整开发规范

**版本**: 1.3  
**日期**: 2025-12-24  
**作者**: Jody  
**状态**: 规划中

---

## 目录

- [一、核心资源分析](#一核心资源分析)
  - [1.1 Claude Cookbooks 关键模块](#11-claude-cookbooks-关键模块)
  - [1.2 Console 元提示词生成器](#12-console-元提示词生成器)
  - [1.3 Prompt Library 模板分类](#13-prompt-library-模板分类)
  - [1.4 Workbench 评估能力](#14-workbench-评估能力)
- [二、架构升级总览](#二架构升级总览)
- [三、新增模块设计](#三新增模块设计)
  - [模块 A：Meta Prompt Engine](#模块-ameta-prompt-engine元提示词引擎)
  - [模块 B：Template Library](#模块-btemplate-library模板库系统)
  - [模块 C：Workbench Integration](#模块-cworkbench-integration工作台集成)
  - [模块 D：Prompt Improver](#模块-dprompt-improver提示词优化器)
- [四、实现步骤 SOP](#四实现步骤-sop)
- [五、文件变更清单](#五文件变更清单)
- [六、里程碑检查点](#六里程碑检查点)
- [七、使用流程示例](#七使用流程示例)

---

## 一、核心资源分析

### 1.1 Claude Cookbooks 关键模块

| 模块 | 路径 | 应用价值 |
|------|------|----------|
| **patterns/agents** | 基础工作流 + 编排器 | Prompt-Chaining、Routing、Orchestrator-Workers |
| **patterns/agents/prompts** | 官方 Prompt 模板 | 高质量 XML 结构参考 |
| **tool_use/memory_cookbook** | 跨会话记忆 | Context Editing 策略 |
| **tool_evaluation** | 工具评估框架 | 评估方法论 |
| **skills** | 文件生成技能 | PPTX/XLSX/DOCX 最佳实践 |

**参考链接**: https://github.com/anthropics/claude-cookbooks

### 1.2 Console 元提示词生成器

**核心技术**:

| 技术 | 说明 |
|------|------|
| **任务分解** | 将 prompt 生成分解为多步骤（定义变量 → 规划结构 → 编写指令） |
| **Few-Shot Learning** | 内置大量任务描述到模板的示例 |
| **XML Spine** | 强结构化 `<instructions>` `<example>` `<formatting>` 标签 |
| **Handlebars 变量** | `{{VARIABLE}}` 占位符标记动态内容 |
| **Chain-of-Thought** | `<scratchpad>` 思考区块 |

**参考链接**: 
- https://www.anthropic.com/news/prompt-generator
- https://www.anthropic.com/news/prompt-improver

### 1.3 Prompt Library 模板分类

| 类别 | 数量 | 典型模板 |
|------|------|----------|
| 代码开发 | 10+ | Python Bug Buster, SQL Sorcerer, Git Gud |
| 数据处理 | 8+ | CSV Converter, Data Organizer, Excel Formula Expert |
| 写作创意 | 12+ | Prose Polisher, Storytelling Sidekick, Alliteration Alchemist |
| 分析推理 | 10+ | Corporate Clairvoyant, Review Classifier, Efficiency Estimator |
| 教育学习 | 8+ | Lesson Planner, Socratic Sage, Second-Grade Simplifier |
| 其他专业 | 10+ | Dream Interpreter, Ethical Dilemma Navigator, Career Coach |

**参考链接**: https://docs.anthropic.com/en/prompt-library/library

### 1.4 Workbench 评估能力

| 功能 | 说明 |
|------|------|
| **Test Case Generation** | 自动生成测试用例（点击按钮） |
| **Side-by-Side Comparison** | 并排比较多个 prompt 版本 |
| **5-Point Grading** | 1-5 分质量评分 |
| **Prompt Versioning** | 版本管理，快速迭代 |
| **Ideal Output Column** | 基准输出对比 |
| **Code Export** | 导出 Python/TypeScript SDK 代码 |

**参考链接**: 
- https://www.anthropic.com/news/evaluate-prompts
- https://docs.anthropic.com/en/docs/test-and-evaluate/eval-tool

---

## 二、架构升级总览

### 现有架构 (v1.2)

```
Router → Pipeline (4 Stages) → Evaluator → Memory
```

### 升级架构 (v1.3)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     升级架构 (v1.3)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              1. Meta Prompt Engine (元提示词引擎)                 │   │
│   │                                                                  │   │
│   │   参考 Console Prompt Generator 架构：                           │   │
│   │   • 任务分解：定义变量 → 规划结构 → 编写指令                      │   │
│   │   • XML Spine 生成：自动添加 <instructions> <example> 等标签     │   │
│   │   • Handlebars 变量注入：{{CONTEXT}} {{TASK}} {{CODE}}           │   │
│   │   • Chain-of-Thought 区块：<scratchpad> <thinking>               │   │
│   │                                                                  │   │
│   └──────────────────────────┬──────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              2. Template Library (模板库系统)                     │   │
│   │                                                                  │   │
│   │   按场景组织的高质量 XML 模板：                                   │   │
│   │   • coding/: bug_fix.xml, refactor.xml, test.xml                │   │
│   │   • data/: csv_process.xml, excel_formula.xml                   │   │
│   │   • writing/: technical_doc.xml, creative.xml                   │   │
│   │   • analysis/: code_review.xml, security_audit.xml              │   │
│   │                                                                  │   │
│   └──────────────────────────┬──────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              3. Workbench Integration (工作台集成)                │   │
│   │                                                                  │   │
│   │   本地模拟 Console Workbench 能力：                              │   │
│   │   • Test Case Generator：自动生成测试用例                        │   │
│   │   • Variant Comparator：并排比较多个增强版本                     │   │
│   │   • Quality Grader：5 分制质量评分                               │   │
│   │   • Version Manager：prompt 版本管理                             │   │
│   │   • Export Generator：导出可执行代码                             │   │
│   │                                                                  │   │
│   └──────────────────────────┬──────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              4. Prompt Improver (提示词优化器)                    │   │
│   │                                                                  │   │
│   │   参考 Console Prompt Improver：                                 │   │
│   │   • Chain-of-Thought 注入：添加系统性思考区块                    │   │
│   │   • Example Standardization：将示例转为一致的 XML 格式           │   │
│   │   • Example Enrichment：为示例添加推理过程                       │   │
│   │   • Prefill Addition：预填充 Assistant 消息                      │   │
│   │   • Iterative Feedback：基于反馈循环优化                         │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三、新增模块设计

### 模块 A：Meta Prompt Engine（元提示词引擎）

**参考来源**: Console Prompt Generator + [Colab Notebook](https://colab.research.google.com/github/anthropics/anthropic-cookbook/blob/main/misc/prompt_generator.ipynb)

**职责**: 将自然语言任务描述转化为结构化 XML prompt

#### 核心流程

```
用户输入: "帮我写一个代码审查提示词"
           │
           ▼
┌─────────────────────────────────────────┐
│ Step 1: 变量识别                         │
│ • 识别需要的输入变量                      │
│ • 输出: [CODE, LANGUAGE, CONTEXT]        │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Step 2: 结构规划                         │
│ • 规划 prompt 的逻辑结构                  │
│ • 决定需要哪些 XML 区块                   │
│ • 输出: [role, context, task, format]   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Step 3: 指令编写                         │
│ • 编写每个区块的具体内容                  │
│ • 添加 Chain-of-Thought                  │
│ • 插入 Few-Shot 示例                     │
│ • 输出: 完整的 XML prompt                │
└─────────────────────────────────────────┘
```

#### XML 结构模板

```xml
<prompt_template>
  <role>
    你是一位专业的代码审查专家...
  </role>
  
  <context>
    项目技术栈: {{TECH_STACK}}
    代码风格规范: {{CODE_STYLE}}
  </context>
  
  <input_data>
    <code language="{{LANGUAGE}}">
      {{CODE}}
    </code>
  </input_data>
  
  <instructions>
    请按以下步骤进行代码审查:
    1. 在 <scratchpad> 中分析代码结构
    2. 识别潜在问题
    3. 提供改进建议
  </instructions>
  
  <scratchpad>
    [思考区域]
  </scratchpad>
  
  <output_format>
    <issues>
      <issue severity="high|medium|low">
        <location>行号</location>
        <description>问题描述</description>
        <suggestion>建议修改</suggestion>
      </issue>
    </issues>
  </output_format>
  
  <examples>
    <example>
      <input>...</input>
      <ideal_output>...</ideal_output>
    </example>
  </examples>
</prompt_template>
```

#### 核心 Meta Prompt 模板

```xml
<meta_prompt>
<role>
你是一个专业的 Prompt 工程师，擅长将任务描述转化为高质量的结构化提示词。
</role>

<task>
用户将提供一个任务描述，请生成一个针对该任务的高质量 prompt 模板。
</task>

<process>
按以下步骤生成 prompt：

1. **变量识别**
   在 <variables> 标签中列出需要的输入变量

2. **结构规划**
   在 <structure> 标签中规划 prompt 的逻辑结构

3. **指令编写**
   在 <prompt_template> 标签中输出最终的 prompt
</process>

<guidelines>
- 使用 XML 标签分隔不同部分
- 添加 <scratchpad> 用于思考过程
- 变量使用 {{VARIABLE}} 格式
- 长变量用 XML 标签包裹
- 提供至少一个 <example>
- 明确指定 <output_format>
</guidelines>

<task_description>
{{TASK_DESCRIPTION}}
</task_description>
</meta_prompt>
```

---

### 模块 B：Template Library（模板库系统）

**参考来源**: Anthropic Prompt Library (50+ 模板)

**职责**: 提供场景化的高质量 XML 模板

#### 目录结构

```
templates/
├── coding/
│   ├── bug_buster.yaml           # Python Bug 修复
│   ├── code_reviewer.yaml        # 代码审查
│   ├── refactor_guide.yaml       # 重构指南
│   ├── test_generator.yaml       # 测试生成
│   └── sql_sorcerer.yaml         # SQL 查询优化
│
├── data/
│   ├── csv_converter.yaml        # 格式转换
│   ├── excel_formula.yaml        # Excel 公式
│   ├── data_organizer.yaml       # 数据整理
│   └── json_transformer.yaml     # JSON 处理
│
├── writing/
│   ├── prose_polisher.yaml       # 文案润色
│   ├── technical_doc.yaml        # 技术文档
│   ├── api_doc.yaml              # API 文档
│   └── readme_generator.yaml     # README 生成
│
├── analysis/
│   ├── code_audit.yaml           # 代码审计
│   ├── security_review.yaml      # 安全审查
│   ├── performance_analysis.yaml # 性能分析
│   └── dependency_check.yaml     # 依赖检查
│
├── meta/
│   ├── prompt_generator.yaml     # 元提示词生成器
│   └── prompt_improver.yaml      # 提示词优化器
│
└── custom/
    └── [用户自定义模板]
```

#### 模板标准格式

```yaml
# templates/coding/code_reviewer.yaml

metadata:
  name: "Code Reviewer"
  category: "coding"
  description: "专业代码审查模板"
  variables:
    - name: "CODE"
      type: "code"
      required: true
    - name: "LANGUAGE"
      type: "string"
      default: "python"
    - name: "CONTEXT"
      type: "text"
      required: false

template: |
  <role>
  你是一位资深的 {{LANGUAGE}} 代码审查专家，拥有 10 年以上的软件开发经验。
  </role>

  <context>
  {{#if CONTEXT}}
  项目背景: {{CONTEXT}}
  {{/if}}
  </context>

  <code_to_review>
  ```{{LANGUAGE}}
  {{CODE}}
  ```
  </code_to_review>

  <instructions>
  请从以下维度进行代码审查：
  
  1. **代码质量**
     - 可读性和命名规范
     - 代码结构和组织
     - 注释和文档
  
  2. **潜在问题**
     - Bug 和逻辑错误
     - 边界条件处理
     - 异常处理
  
  3. **性能考量**
     - 算法复杂度
     - 资源使用
     - 可优化点
  
  4. **安全隐患**
     - 输入验证
     - 敏感数据处理
     - 常见漏洞
  </instructions>

  <scratchpad>
  首先，让我分析这段代码的整体结构和目的...
  </scratchpad>

  <output_format>
  请按以下格式输出审查结果：
  
  ## 总体评价
  [简短的总体评价]
  
  ## 问题列表
  | 严重程度 | 位置 | 问题描述 | 建议修改 |
  |---------|------|---------|---------|
  
  ## 优点
  [代码的亮点]
  
  ## 改进建议
  [具体的改进建议]
  </output_format>

examples:
  - input:
      CODE: |
        def calc(x):
          return x*2+1
      LANGUAGE: "python"
    ideal_output: |
      ## 总体评价
      代码功能简单但存在可读性问题。
      
      ## 问题列表
      | 严重程度 | 位置 | 问题描述 | 建议修改 |
      |---------|------|---------|---------|
      | 中 | 函数名 | 命名不清晰 | 改为 `double_plus_one` |
      | 低 | 参数 | 缺少类型提示 | 添加 `x: int` |
```

#### 模板匹配规则

```yaml
template_matching:
  coding/bug_buster:
    keywords: ["修复", "bug", "错误", "异常", "崩溃"]
    file_patterns: ["*.py", "*.js", "*.ts"]
    
  coding/code_reviewer:
    keywords: ["审查", "review", "检查", "评审"]
    context_hints: ["code review", "pull request"]
    
  coding/test_generator:
    keywords: ["测试", "test", "单元测试", "集成测试"]
    file_patterns: ["test_*.py", "*_test.py"]
    
  data/excel_formula:
    keywords: ["excel", "公式", "表格", "spreadsheet"]
    
  writing/technical_doc:
    keywords: ["文档", "说明", "documentation"]
    context_hints: ["API", "接口", "使用说明"]
```

---

### 模块 C：Workbench Integration（工作台集成）

**参考来源**: Anthropic Console Workbench

**职责**: 本地模拟 Console 的测试评估能力

#### C.1 Test Case Generator（测试用例生成器）

**功能**: 自动生成多样化的测试输入

| 策略 | 说明 | 示例 |
|------|------|------|
| 边界值 | 极端情况 | 空输入、超长输入、特殊字符 |
| 等价类 | 典型场景 | 正常代码、带 bug 代码、复杂代码 |
| 领域特定 | 业务相关 | 不同编程语言、不同框架 |
| 对抗性 | 挑战性输入 | 混淆代码、恶意输入 |

#### C.2 Variant Comparator（变体比较器）

**功能**: 并排比较多个 prompt 版本的输出

| 维度 | 权重 | 评估方法 |
|------|------|----------|
| 完整性 | 25% | 是否覆盖所有要求的输出项 |
| 准确性 | 30% | 输出内容是否正确 |
| 格式一致性 | 15% | 是否符合指定格式 |
| 响应时间 | 10% | 生成速度 |
| Token 效率 | 10% | Token 使用量 |
| 用户偏好 | 10% | 历史偏好匹配 |

#### C.3 Quality Grader（质量评分器）

**功能**: 5 分制质量评分

| 分数 | 等级 | 标准 |
|------|------|------|
| 5 | 优秀 | 完全符合要求，可直接使用 |
| 4 | 良好 | 基本符合要求，需微调 |
| 3 | 合格 | 部分符合要求，需较多修改 |
| 2 | 较差 | 大部分不符合要求 |
| 1 | 失败 | 完全不符合要求 |

#### C.4 Version Manager（版本管理器）

**功能**: 管理 prompt 迭代版本

```yaml
prompt_versions:
  - version: "1.0.0"
    created_at: "2025-12-24"
    template_hash: "abc123"
    test_results:
      passed: 8
      failed: 2
      avg_score: 4.2
    
  - version: "1.1.0"
    created_at: "2025-12-25"
    template_hash: "def456"
    parent: "1.0.0"
    changes:
      - "添加了 Chain-of-Thought"
      - "优化了输出格式"
    test_results:
      passed: 9
      failed: 1
      avg_score: 4.6
```

---

### 模块 D：Prompt Improver（提示词优化器）

**参考来源**: Console Prompt Improver

**职责**: 自动优化现有 prompt

#### 优化技术

| 技术 | 说明 | 效果 |
|------|------|------|
| **Chain-of-Thought 注入** | 添加 `<scratchpad>` 思考区块 | 提升推理准确性 |
| **Example Standardization** | 将示例转为一致的 XML 格式 | 提升格式一致性 |
| **Example Enrichment** | 为示例添加推理过程 | 提升学习效果 |
| **Prefill Addition** | 预填充 Assistant 消息开头 | 强制输出格式 |
| **Instruction Clarity** | 重写模糊指令 | 减少歧义 |
| **Variable Tagging** | 用 XML 包裹长变量 | 清晰边界 |

#### 优化流程

```
原始 Prompt
    │
    ├── 1. 结构分析
    │   └── 识别缺失的区块
    │
    ├── 2. Chain-of-Thought 注入
    │   └── 添加 <scratchpad> 或 <thinking>
    │
    ├── 3. 示例标准化
    │   └── 转为 <example><input>...<output>...</example>
    │
    ├── 4. 变量标记
    │   └── 长变量用 XML 包裹
    │
    ├── 5. 指令重写
    │   └── 消除歧义，添加细节
    │
    └── 6. 输出优化后的 Prompt
```

#### 优化效果指标

参考 Anthropic 测试结果：

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 分类准确率 | ~60% | ~90% | +30% |
| 格式遵守率 | ~70% | 100% | +30% |
| 字数控制 | ~75% | 100% | +25% |

---

## 四、实现步骤 SOP

### 阶段 1：Meta Prompt Engine（Day 1-3）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 1.1 | 创建 `meta_prompt_engine.py` | 文件存在 |
| 1.2 | 实现变量识别逻辑 | 从任务描述提取变量 |
| 1.3 | 实现结构规划逻辑 | 决定 XML 区块组成 |
| 1.4 | 实现指令编写逻辑 | 生成具体内容 |
| 1.5 | 实现 XML 组装 | 输出格式化 XML |
| 1.6 | 集成到增强流程 | 替代简单字符串拼接 |
| 1.7 | 添加测试 | 多种任务类型测试 |

### 阶段 2：Template Library（Day 4-6）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 2.1 | 设计模板 YAML schema | 统一格式定义 |
| 2.2 | 创建 coding 类模板（5 个） | 代码审查、Bug 修复、重构、测试、SQL |
| 2.3 | 创建 data 类模板（4 个） | CSV、Excel、JSON、数据整理 |
| 2.4 | 创建 writing 类模板（4 个） | 技术文档、API 文档、README |
| 2.5 | 创建 analysis 类模板（4 个） | 审计、安全、性能、依赖 |
| 2.6 | 创建 meta 类模板（2 个） | 生成器、优化器 |
| 2.7 | 实现模板加载器 | 读取、解析、渲染 |
| 2.8 | 实现模板匹配器 | 根据任务选择模板 |
| 2.9 | 添加测试 | 每个模板至少 2 个测试用例 |

### 阶段 3：Workbench Integration（Day 7-10）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 3.1 | 创建 `workbench/` 目录结构 | 模块化组织 |
| 3.2 | 实现 Test Case Generator | 自动生成测试用例 |
| 3.3 | 实现 Variant Comparator | 并排比较输出 |
| 3.4 | 实现 Quality Grader | 5 分制评分 |
| 3.5 | 实现 Version Manager | 版本管理 |
| 3.6 | 实现 Export Generator | 导出代码 |
| 3.7 | 创建 Workbench CLI | `pe workbench` 命令 |
| 3.8 | 添加测试 | 各子模块测试 |

### 阶段 4：Prompt Improver（Day 11-13）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 4.1 | 创建 `prompt_improver.py` | 文件存在 |
| 4.2 | 实现 Chain-of-Thought 注入 | 自动添加思考区块 |
| 4.3 | 实现 Example Standardization | 示例格式标准化 |
| 4.4 | 实现 Example Enrichment | 为示例添加推理 |
| 4.5 | 实现 Prefill Addition | 预填充 Assistant |
| 4.6 | 实现 Instruction Clarity | 重写模糊指令 |
| 4.7 | 实现 Variable Tagging | XML 变量标记 |
| 4.8 | 实现反馈循环 | 基于用户反馈迭代 |
| 4.9 | 创建 `pe improve` 命令 | CLI 集成 |
| 4.10 | 添加测试 | 优化前后对比测试 |

### 阶段 5：CLI 增强（Day 14-15）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 5.1 | 添加 `pe generate` 命令 | 从描述生成 prompt |
| 5.2 | 添加 `pe improve` 命令 | 优化现有 prompt |
| 5.3 | 添加 `pe template` 命令 | 模板管理 |
| 5.4 | 添加 `pe workbench` 命令 | 工作台功能 |
| 5.5 | 更新帮助文档 | `pe --help` |
| 5.6 | 更新 README | 新功能说明 |

#### 新 CLI 命令

```bash
# 元提示词生成
pe generate "帮我写一个代码审查工具的提示词"
pe generate --template meta/prompt_generator.xml

# 提示词优化
pe improve input_prompt.txt --output improved.txt
pe improve --add-cot          # 添加 Chain-of-Thought
pe improve --standardize      # 标准化示例
pe improve --all              # 应用所有优化

# 模板管理
pe template list              # 列出所有模板
pe template show coding/code_reviewer  # 查看模板
pe template render coding/code_reviewer --vars vars.yaml  # 渲染模板
pe template create --category coding --name my_template   # 创建模板

# 工作台
pe workbench generate-tests "任务描述" --count 10
pe workbench run-tests --prompt prompt.yaml
pe workbench compare v1 v2
pe workbench grade --input in.txt --output out.txt
pe workbench versions
pe workbench export --format python
```

### 阶段 6：测试与发布（Day 16-17）

| 步骤 | 任务 | 验收标准 |
|------|------|----------|
| 6.1 | Meta Prompt Engine 测试 | 多种任务类型 |
| 6.2 | Template Library 测试 | 每个模板 2+ 用例 |
| 6.3 | Workbench 测试 | 各子模块功能 |
| 6.4 | Prompt Improver 测试 | 优化效果验证 |
| 6.5 | 端到端测试 | 完整流程 |
| 6.6 | 性能测试 | 响应时间 |
| 6.7 | 更新文档 | 完整文档 |
| 6.8 | 发布 v1.3 | GitHub Release |

---

## 五、文件变更清单

### 新增文件

```
meta_prompt_engine.py              # 元提示词引擎
prompt_improver.py                 # 提示词优化器

workbench/
├── __init__.py
├── test_generator.py              # 测试用例生成器
├── variant_comparator.py          # 变体比较器
├── quality_grader.py              # 质量评分器
├── version_manager.py             # 版本管理器
└── export_generator.py            # 导出生成器

templates/
├── coding/
│   ├── bug_buster.yaml
│   ├── code_reviewer.yaml
│   ├── refactor_guide.yaml
│   ├── test_generator.yaml
│   └── sql_sorcerer.yaml
├── data/
│   ├── csv_converter.yaml
│   ├── excel_formula.yaml
│   ├── data_organizer.yaml
│   └── json_transformer.yaml
├── writing/
│   ├── prose_polisher.yaml
│   ├── technical_doc.yaml
│   ├── api_doc.yaml
│   └── readme_generator.yaml
├── analysis/
│   ├── code_audit.yaml
│   ├── security_review.yaml
│   ├── performance_analysis.yaml
│   └── dependency_check.yaml
├── meta/
│   ├── prompt_generator.yaml
│   └── prompt_improver.yaml
└── schema.yaml                    # 模板 schema 定义

tests/
├── test_meta_prompt_engine.py
├── test_prompt_improver.py
├── test_workbench/
│   ├── test_test_generator.py
│   ├── test_variant_comparator.py
│   ├── test_quality_grader.py
│   └── test_version_manager.py
└── test_templates/
    ├── test_coding_templates.py
    ├── test_data_templates.py
    └── test_writing_templates.py
```

### 修改文件

```
enhanced_prompt_generator.py       # 集成 Meta Prompt Engine
router.py                          # 集成模板匹配
evaluator.py                       # 集成 Quality Grader
requirements.txt                   # 新依赖
README.md                          # 更新文档
```

---

## 六、里程碑检查点

| 里程碑 | 时间 | 验收标准 |
|--------|------|----------|
| M1 | Day 3 | Meta Prompt Engine 能生成 XML 结构 |
| M2 | Day 6 | Template Library 包含 20+ 模板 |
| M3 | Day 10 | Workbench 5 个子模块可用 |
| M4 | Day 13 | Prompt Improver 优化效果 >20% |
| M5 | Day 15 | 新 CLI 命令全部可用 |
| M6 | Day 17 | v1.3 发布就绪 |

---

## 七、使用流程示例

### 场景 1：从描述生成 Prompt

```bash
$ pe generate "帮我写一个代码审查提示词，需要检查 Python 代码的质量和安全性"

[Meta Prompt Engine] 分析任务描述...
  → 识别变量: CODE, LANGUAGE, CONTEXT
  → 规划结构: role + context + instructions + scratchpad + output_format + examples
  → 生成模板...

════════════════════════════════════════════
<prompt_template>
  <role>
  你是一位资深的 Python 代码审查专家...
  </role>
  
  <context>
  项目背景: {{CONTEXT}}
  </context>
  
  <code_to_review>
  ```python
  {{CODE}}
  ```
  </code_to_review>
  
  <instructions>
  请从以下维度进行代码审查：
  1. 代码质量（可读性、命名、结构）
  2. 潜在问题（Bug、边界条件、异常处理）
  3. 安全隐患（输入验证、敏感数据、常见漏洞）
  </instructions>
  
  <scratchpad>
  首先，让我分析这段代码的整体结构...
  </scratchpad>
  
  <output_format>
  ## 总体评价
  ## 问题列表
  ## 改进建议
  </output_format>
</prompt_template>
════════════════════════════════════════════

是否保存为模板？[Y/n] y
模板名称: my_code_reviewer
已保存到: templates/custom/my_code_reviewer.yaml
```

### 场景 2：优化现有 Prompt

```bash
$ pe improve old_prompt.txt

[Prompt Improver] 分析原始 prompt...

发现可优化项：
  ⚠ 缺少 Chain-of-Thought 区块
  ⚠ 示例格式不一致
  ⚠ 变量未用 XML 标记
  ⚠ 输出格式不明确

正在优化...

优化完成！
  + 添加了 <scratchpad> 思考区块
  + 标准化了 2 个示例
  + 用 <code> 包裹了代码变量
  + 添加了 <output_format> 定义

预估效果提升: +28%

查看优化后的 prompt？[Y/n] y
保存到文件？[Y/n] y
已保存到: improved_prompt.txt
```

### 场景 3：Workbench 测试评估

```bash
$ pe workbench run-tests --prompt templates/coding/code_reviewer.yaml

[Workbench] 加载模板: code_reviewer
[Workbench] 生成测试用例...

  生成 10 个测试用例：
  #1 正常 Python 代码
  #2 带 bug 的代码
  #3 安全漏洞代码
  #4 复杂嵌套代码
  #5 空输入
  ...

[Workbench] 运行测试...

测试结果：
┌────┬──────────────┬───────┬──────────────────┐
│ #  │ 测试用例      │ 分数  │ 备注              │
├────┼──────────────┼───────┼──────────────────┤
│ 1  │ 正常代码      │ 5     │ 完美              │
│ 2  │ 带 bug 代码   │ 4     │ 识别到 bug        │
│ 3  │ 安全漏洞      │ 5     │ 识别到漏洞        │
│ 4  │ 复杂嵌套      │ 3     │ 分析不够深入      │
│ 5  │ 空输入        │ 4     │ 正确处理边界      │
└────┴──────────────┴───────┴──────────────────┘

平均分: 4.2/5
通过率: 90%

保存结果？[Y/n] y
已保存到: .pe-workbench/results/code_reviewer_2025-12-25.json
```

---

## 附录

### A. 参考资源

| 资源 | 链接 |
|------|------|
| Claude Cookbooks | https://github.com/anthropics/claude-cookbooks |
| Prompt Library | https://docs.anthropic.com/en/prompt-library/library |
| Console Prompt Generator | https://www.anthropic.com/news/prompt-generator |
| Console Prompt Improver | https://www.anthropic.com/news/prompt-improver |
| Workbench Evaluation | https://www.anthropic.com/news/evaluate-prompts |
| XML Tags Best Practice | https://docs.anthropic.com/en/docs/use-xml-tags |

### B. 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2025-12 | 初始版本，P0.1-P0.6 |
| v1.1 | 2025-12 | Agent Docs Parser, Clarity Scorer, Clarifier |
| v1.2 | 2025-12 | Router, Pipeline, Evaluator, Memory |
| v1.3 | 计划中 | Meta Prompt Engine, Template Library, Workbench, Improver |

---

*文档结束*
