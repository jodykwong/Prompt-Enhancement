# Prompt Enhancement v1.1 - BMAD Brownfield Level 迭代指南

**版本**: 1.0
**日期**: 2025-12-15
**作者**: Jodykwong + BMAD Team
**用途**: 按BMAD brownfield level规范化迭代Prompt Enhancement v1.1

---

## 目录

1. [BMAD Brownfield Level 概念](#bmad-brownfield-level-概念)
2. [项目现状评估](#项目现状评估)
3. [Level 2 → 2.5 迭代计划（P0）](#level-2--25-迭代计划p0)
4. [Level 2.5 → 3.0 进化路线（P1）](#level-25--30-进化路线p1)
5. [Level 3 优化方向（长期）](#level-3-优化方向长期)
6. [检查清单](#检查清单)

---

## BMAD Brownfield Level 概念

### 什么是Brownfield Level？

在BMAD方法论中，"brownfield"指有既有代码基础的项目。根据成熟度分为5个等级：

| Level | 名称 | 特征 | 适用场景 |
|-------|------|------|--------|
| **1** | 全新项目（Greenfield） | 无既有代码 | 项目启动阶段 |
| **2** | 基础棕地 | 有核心功能，需理解和改进 | 早期产品版本 |
| **2.5** | 结构化棕地 | 代码组织清晰，质量控制引入 | 准备扩展阶段 |
| **3** | 成熟棕地 | 完整的测试、监控、文档体系 | 稳定运维阶段 |
| **4+** | 企业级棕地 | 分布式治理、自动化运维、高可用 | 大规模商业应用 |

### Prompt Enhancement 当前处于 Level 2

**现状特征：**
- ✅ v1.01 有完整的核心功能管道
- ✅ 代码结构清晰（detector → collector → generator）
- ⚠️ 缺乏灵活性（只支持统一规范）
- ⚠️ 缺乏质量控制（Clarity Scoring）
- ⚠️ 缺乏缓存优化
- ⚠️ 文档和测试不够完整

**升级目标：**
- 第一阶段：晋升到 Level 2.5（支持异质化项目 + 基础质量控制）
- 第二阶段：晋升到 Level 3（完整测试 + 高级缓存 + 企业级文档）

---

## 项目现状评估

### 代码结构分析

```
当前架构 (v1.01)：
┌─────────────────────────────────────┐
│    Enhanced Prompt System v1.01     │
├─────────────────────────────────────┤
│  [Tech Stack Detector]              │
│         ↓                            │
│  [Project Structure Analyzer]       │
│         ↓                            │
│  [Git History Analyzer]             │
│         ↓                            │
│  [Context Collector] ← 单一数据源   │
│         ↓                            │
│  [Prompt Generator]                 │
│         ↓                            │
│  [Output] → Markdown/Plain          │
└─────────────────────────────────────┘
```

### DESIGN_V1.1 的增强建议

```
升级架构 (v1.1)：
┌──────────────────────────────────────────┐
│   Enhanced Prompt System v1.1            │
├──────────────────────────────────────────┤
│  ┌─ [Agent Docs Parser] ← 新增          │
│  ├─ [Clarity Scorer]    ← 新增          │
│  └─ [Clarifier]         ← 可选          │
│         ↓                                 │
│  [Context Collector] ← 升级（多源）    │
│         ├─ Tech Stack                    │
│         ├─ Project Structure             │
│         ├─ Git History                   │
│         └─ AGENTS.md Config ← 新增      │
│         ↓                                 │
│  [Prompt Generator] ← 升级              │
│         ├─ Project Norms (来自AGENTS.md)│
│         ├─ Boundary Constraints (⚠️)    │
│         ├─ Special Warnings (🚨)        │
│         └─ [Cache Layer] ← P1 可选      │
│         ↓                                 │
│  [Output] → Markdown/Plain              │
└──────────────────────────────────────────┘
```

### 质量现状评估

| 维度 | 当前状态 | 目标(v1.1) | 目标(v1.2+) |
|------|--------|-----------|-----------|
| 代码覆盖率 | ~60% | 80%+ | 90%+ |
| 文档完整度 | 基础 | 详细(API+用户指南) | 企业级 |
| 性能优化 | 无缓存 | 基础缓存 | 向量缓存+ML |
| 错误处理 | 基础 | 完善 | 生产监控 |
| 版本管理 | 手动 | 自动化(CI/CD) | 金丝雀发布 |

---

## Level 2 → 2.5 迭代计划（P0）

### 阶段目标

**时间**: Day 1-3（3天）
**成果**: 可交付的 v1.1.0-alpha
**范围**: P0功能（必做，无可选项）

### 核心原则

1. **最小化风险** - 新代码与旧代码隔离
2. **快速迭代** - 每天一个可测试的增量
3. **文档驱动** - 先文档后代码
4. **测试优先** - 每个新模块都有单元测试

### 分日程表

#### Day 1：规范化 + Agent Docs Parser 核心

**主要任务：**

```yaml
早晨会议:
  - 确认设计评审（设计文档已评审 ✓）
  - 确认API contracts
  - 分配代码审查人

任务 1.1：创建项目结构（1h）
  文件:
    src/v1_1/
    ├── __init__.py
    ├── agent_docs_parser.py     # 新建
    ├── models.py                # 新建（数据类）
    └── core/
        ├── collector_v11.py     # 升级版 collector
        └── generator_v11.py     # 升级版 generator

  验收标准:
    ✓ 文件结构创建完成
    ✓ 可以 import 所有模块（无语法错误）

任务 1.2：定义数据模型（1h）
  文件: src/v1_1/models.py
  内容:
    @dataclass AgentConfig
    @dataclass CodeBlock
    @dataclass EnhancementContext
    @dataclass EnhancedPrompt

  验收标准:
    ✓ 所有数据类定义完整
    ✓ type hints 完整
    ✓ 可以序列化/反序列化

任务 1.3：实现 Agent Docs Parser - 基础（2h）
  文件: src/v1_1/agent_docs_parser.py
  范围:
    ✓ find_config_file() - 搜索AGENTS.md
    ✓ detect_format() - 检测结构化/灵活格式
    ✓ parse() - 主解析方法
    ✓ 异常处理 - graceful degradation

  验收标准:
    ✓ 可以找到test_agents.md
    ✓ 正确识别两种格式
    ✓ 返回有效的AgentConfig
    ✓ 缺失文件返回empty config而非crash

任务 1.4：单元测试 - Parser（1.5h）
  文件: tests/v1_1/test_agent_docs_parser.py
  测试用例:
    ✓ test_find_config_file_exists
    ✓ test_find_config_file_missing
    ✓ test_detect_format_structured
    ✓ test_detect_format_flexible
    ✓ test_parse_valid_file
    ✓ test_parse_missing_file

  验收标准:
    ✓ 所有6个测试通过
    ✓ 覆盖率 >= 85%

午餐后:
  代码审查（30m）
    - 2人代码审查
    - 检查点：
      ✓ 错误处理完善
      ✓ 类型提示完整
      ✓ 代码风格一致
      ✓ 文档字符串清晰

总结:
  - 交付: Agent Docs Parser（完整可用）
  - 时间: 6h
  - 验收: Day 1 checklist 全通过
```

#### Day 2：Context Collector 升级 + Prompt Generator 升级

**主要任务：**

```yaml
早晨会议:
  - review Day 1 deliverables
  - 确认升级策略（backward compatibility）

任务 2.1：升级 Context Collector（2h）
  文件: src/v1_1/collector_v11.py
  改动:
    原始方法:
      collect(project_root) → EnhancementContext

    升级后:
      同样的签名，但EnhancementContext新增:
        + agents_config: AgentConfig  # 来自Agent Docs Parser
        + clarity_score: float         # 来自Clarity Scorer（暂时固定值）

  实现细节:
    1. 调用Agent Docs Parser找到并解析AGENTS.md
    2. 如果找不到AGENTS.md，使用default config
    3. 计算clarity_score（现在还是placeholder = 0.5）
    4. 保留现有所有逻辑（tech_stack, project_structure等）

  验收标准:
    ✓ 返回完整的EnhancementContext
    ✓ 包含agents_config字段
    ✓ 向后兼容（旧代码仍可用）
    ✓ 处理缺失AGENTS.md的情况

任务 2.2：升级 Prompt Generator（2h）
  文件: src/v1_1/generator_v11.py
  改动:
    原始输出:
      ┌─────────────────────┐
      │ Project Context     │
      │ Relevant Files      │
      │ Code Snippets       │
      │ Best Practices      │
      └─────────────────────┘

    升级后:
      ┌─────────────────────┐
      │ Project Norms ← NEW │  # 来自AGENTS.md
      │ Boundary Constraints│  # ← NEW （⚠️标记）
      │ Special Warnings    │  # ← NEW （🚨标记）
      │ Project Context     │  # 现有
      │ Relevant Files      │  # 现有
      │ Code Snippets       │  # 现有
      │ Best Practices      │  # 现有
      └─────────────────────┘

  实现细节:
    generate(context: EnhancementContext) → EnhancedPrompt:
      1. 从 context.agents_config 提取：
         - commands → "Project Norms" section
         - guidelines → "Project Norms" section
         - boundaries → "Boundary Constraints" section (⚠️)
         - warnings → "Special Warnings" section (🚨)
      2. 保留现有所有输出逻辑
      3. 调整格式，新section插在最前面

  验收标准:
    ✓ 返回EnhancedPrompt对象
    ✓ 包含3个新字段：project_norms, boundary_constraints, special_warnings
    ✓ 输出包含✅标记的project norms
    ✓ 输出包含⚠️标记的boundary constraints
    ✓ 输出包含🚨标记的special warnings

任务 2.3：集成测试（1.5h）
  文件: tests/v1_1/test_integration_v11.py
  测试场景:
    ✓ test_e2e_with_agents_md
      输入: 项目根目录（包含AGENTS.md）
      输出: 完整的增强prompt，包含新增的3个section

    ✓ test_e2e_without_agents_md
      输入: 项目根目录（无AGENTS.md）
      输出: 完整的增强prompt，使用默认config

    ✓ test_backward_compatibility
      验证: 旧代码仍能使用新版本

  验收标准:
    ✓ 所有3个集成测试通过
    ✓ 覆盖率 >= 80%

午餐后:
  性能测试（1h）
    - AGENTS.md 解析 < 100ms
    - Context collect < 500ms
    - Prompt generation < 200ms
    - 总时间 < 1s

  代码审查（1h）
    - 3人轮流审查
    - 重点：backward compatibility, 错误处理

总结:
  - 交付: 完整的升级pipeline（Collector + Generator）
  - 时间: 6.5h
  - 验收: Day 2 checklist 全通过
```

#### Day 3：文档 + 发布准备

**主要任务：**

```yaml
早晨会议:
  - 确认v1.1.0-alpha发布检查清单

任务 3.1：API 文档（1.5h）
  文件: docs/API_V1.1.md
  内容:
    1. AgentDocParser 完整API（含示例）
    2. 升级后的Context Collector API
    3. 升级后的Prompt Generator API
    4. 新增的数据类说明
    5. 向后兼容性说明
    6. 错误处理指南

  验收标准:
    ✓ 每个public method都有说明和示例
    ✓ 数据结构都有字段说明
    ✓ 有troubleshooting section

任务 3.2：用户指南（1h）
  文件: docs/AGENTS_MD_GUIDE.md
  内容:
    1. 什么是AGENTS.md
    2. 如何在你的项目中创建AGENTS.md
    3. 支持的两种格式（结构化vs灵活）
    4. 最佳实践（✅应该做什么）
    5. 常见错误（⚠️不应该做什么）
    6. 示例（3个）

  验收标准:
    ✓ 新手能按指南创建AGENTS.md
    ✓ 包含实际示例
    ✓ 包含troubleshooting

任务 3.3：代码示例和测试数据（1h）
  文件: examples/
  创建:
    ├── AGENTS_structured.md    # 结构化格式示例
    ├── AGENTS_flexible.md      # 灵活格式示例
    └── sample_project/         # 完整项目示例
        ├── AGENTS.md
        ├── src/
        ├── tests/
        └── README.md

  验收标准:
    ✓ 每个示例都可以被Parser正确解析
    ✓ 覆盖边界情况
    ✓ 可以作为用户参考

任务 3.4：CHANGELOG + README（1h）
  文件: CHANGELOG.md, README.md
  内容:
    CHANGELOG:
      v1.1.0-alpha (2025-12-15)
      - ADDED: Agent Docs Parser with dual format support
      - ADDED: Project norms, boundary constraints, special warnings sections
      - CHANGED: Enhanced Context Collector with agents_config
      - CHANGED: Prompt Generator with new output blocks
      - FIXED: Error handling for missing config files

    README:
      - 更新功能列表
      - 更新安装说明（if any）
      - 更新快速开始
      - 链接到新文档

  验收标准:
    ✓ 所有改变都在CHANGELOG中
    ✓ README清晰反映新功能
    ✓ 安装/使用步骤正确

下午:
  最终检查（2h）
    1. 代码审查（pass/fail）
    2. 文档审查（pass/fail）
    3. 测试覆盖率检查（必须 >= 80%）
    4. 性能检查（必须满足要求）
    5. 安全检查（no hardcoded secrets等）

  发布准备（1h）
    - 创建Git tag: v1.1.0-alpha
    - 生成Release notes
    - 准备部署脚本

总结:
  - 交付: v1.1.0-alpha（完整可用版本）
  - 时间: 7h
  - 验收: 所有检查清单通过
```

### Level 2 → 2.5 的验收标准

```yaml
代码质量:
  ✓ 所有单元测试通过
  ✓ 代码覆盖率 >= 80%
  ✓ 无lint错误（Black, mypy）
  ✓ 所有public methods有文档

文档完整性:
  ✓ API文档（docs/API_V1.1.md）
  ✓ 用户指南（docs/AGENTS_MD_GUIDE.md）
  ✓ 代码示例（examples/）
  ✓ CHANGELOG更新

性能达成:
  ✓ AGENTS.md解析 < 100ms
  ✓ Context collect < 500ms
  ✓ Prompt generation < 200ms
  ✓ 内存使用 < 50MB

功能完整性:
  ✓ Agent Docs Parser（2种格式）
  ✓ Context Collector升级
  ✓ Prompt Generator升级（3个新section）
  ✓ 完整的错误处理

发布准备:
  ✓ v1.1.0-alpha tag创建
  ✓ Release notes编写
  ✓ 3个真实项目测试通过

实现工作量估计: 18-20人小时
```

---

## Level 2.5 → 3.0 进化路线（P1）

### 阶段目标

**时间**: Day 4-6（3天，可选）
**成果**: v1.1.0 稳定版
**范围**: P1功能（质量控制 + 性能优化）

### Day 4：Clarity Scorer 集成

```yaml
任务 4.1：实现 Clarity Scorer（2h）
  文件: src/v1_1/clarity_scorer.py
  内容:
    - ClarityScorer 类（5个评分特征）
    - 评分规则（文件名、函数名、动词、技术术语、范围）
    - 解释器（clear/medium/unclear）

  验收标准:
    ✓ 模糊prompt得分 <= 0.3
    ✓ 明确prompt得分 >= 0.6
    ✓ 中等prompt得分在0.3-0.6之间

任务 4.2：集成 Clarity Scorer 到 Pipeline（1h）
  改动: src/v1_1/collector_v11.py
  逻辑:
    1. 计算clarity_score（不再是placeholder）
    2. 设置clarity_level（clear/medium/unclear）

  验收标准:
    ✓ EnhancementContext.clarity_score 被正确计算
    ✓ 与Agent Docs Parser兼容

任务 4.3：Clarity Scorer 测试（1h）
  文件: tests/v1_1/test_clarity_scorer.py
  用例:
    ✓ test_clear_prompt（>= 0.6）
    ✓ test_unclear_prompt（<= 0.3）
    ✓ test_medium_prompt（0.3-0.6）
    ✓ test_multilingual（中文/英文）

时间: 4h
交付: Clarity Scorer 集成版本
```

### Day 5-6：Response Cache + 高级优化

```yaml
任务 5.1-5.3：Response Cache 系统（4h）
  文件: src/v1_1/response_cache.py
  内容:
    - 3种缓存策略
    - 文件监控（AGENTS.md变更检测）
    - 缓存统计

  验收标准:
    ✓ 缓存命中时间 < 5ms
    ✓ 缓存大小 < 50MB

任务 6.1-6.3：性能优化 + 企业级特性（3h）
  - 向量相似度计算（可选，v1.2）
  - 性能基准测试
  - 监控metrics

  验收标准:
    ✓ 冷启动 < 15s
    ✓ 缓存命中 < 5s
```

### Level 2.5 → 3.0 检查清单

```yaml
功能完整性:
  ✓ Clarity Scorer 完整集成
  ✓ 基础缓存系统
  ✓ 高级性能优化

测试覆盖:
  ✓ 单元测试 >= 85%
  ✓ 集成测试完整
  ✓ 性能测试达成目标

文档完整:
  ✓ 深入的API文档
  ✓ 性能优化指南
  ✓ 故障排除指南

生产就绪:
  ✓ 所有critical paths 有测试
  ✓ 错误处理完善
  ✓ 日志和监控

发布:
  ✓ v1.1.0-rc 候选版本
  ✓ 5个真实项目测试通过
  ✓ 社区反馈整合

实现工作量估计: 15-18人小时（可选）
```

---

## Level 3 优化方向（长期）

### v1.2+ 规划（推荐）

```yaml
v1.2.0 - 高级缓存（向量相似度）:
  工作量: 20h
  特性:
    - sentence-transformers 集成
    - 相似prompt缓存（相似度 > 0.85）
    - 缓存效率分析

  性能目标:
    - 缓存命中率: 20-30%
    - 总体响应时间: 50% 降低

v1.3.0 - ML-based Clarity:
  工作量: 30h
  特性:
    - 训练数据集（100+ 样本）
    - 分类模型（Clarity level）
    - 实时反馈loop

  质量目标:
    - Clarity 预测准确率: > 85%
    - 支持多语言

v1.4.0 - 企业级特性:
  工作量: 40h+
  特性:
    - 权限管理（RBAC）
    - 审计日志
    - 多租户支持
    - SLA 监控
```

---

## 检查清单

### 开发流程清单

```markdown
## Phase 1: 规划（已完成）
- [x] DESIGN_V1.1.md 编写完成
- [x] 本迭代指南编写完成
- [x] Team alignment 完成
- [ ] 技术栈确认（Python版本、依赖）
- [ ] 开发环境准备
- [ ] 代码审查流程确认

## Phase 2: 开发（Day 1-3）

### Day 1 Checklist
- [ ] 创建分支 `feature/v1.1-agent-parser`
- [ ] 项目结构创建完成
- [ ] models.py 所有数据类定义完成
- [ ] AgentDocParser 核心功能完成
- [ ] 单元测试编写完成
- [ ] 代码审查通过
- [ ] Day 1 合并到 develop 分支

### Day 2 Checklist
- [ ] Context Collector 升级完成
- [ ] Prompt Generator 升级完成
- [ ] 集成测试编写完成
- [ ] 性能测试达成目标
- [ ] 代码审查通过
- [ ] Day 2 合并到 develop 分支

### Day 3 Checklist
- [ ] API 文档完写
- [ ] 用户指南完写
- [ ] 示例代码完成
- [ ] CHANGELOG 编写
- [ ] README 更新
- [ ] 所有文档审查通过
- [ ] 最终检查清单通过
- [ ] v1.1.0-alpha tag 创建
- [ ] Release notes 发布

## Phase 3: 验收（Day 3下午）

### 质量关卡
- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 代码覆盖率 >= 80% (`pytest --cov=src`)
- [ ] Lint 无错误 (`black --check src/`, `mypy src/`)
- [ ] 无安全问题 (no secrets, SQL injection等)

### 性能关卡
- [ ] AGENTS.md 解析 < 100ms
- [ ] Context collect < 500ms
- [ ] Prompt generation < 200ms
- [ ] 内存使用 < 50MB

### 文档关卡
- [ ] API 文档清晰完整
- [ ] 用户指南可被新手理解
- [ ] 示例代码可运行
- [ ] CHANGELOG 准确

### 发布关卡
- [ ] 3个真实项目测试通过
- [ ] v1.1.0-alpha 发布到 GitHub
- [ ] 发布说明明确标记为 "alpha"
- [ ] Known issues 列表完整

## Phase 4: 可选升级（Day 4-6，可跳过）

### Clarity Scorer 集成
- [ ] ClarityScorer 实现完成
- [ ] 集成到 pipeline
- [ ] 单元测试完成
- [ ] 集成测试完成

### Response Cache
- [ ] 缓存系统实现
- [ ] 文件监控实现
- [ ] 性能测试达成
- [ ] 生产就绪

### 最终发布
- [ ] v1.1.0-rc 创建
- [ ] v1.1.0 稳定版发布

## Phase 5: 长期规划（v1.2+）

- [ ] v1.2.0 需求评审
- [ ] v1.3.0 ML 模型准备
- [ ] v1.4.0 企业特性规划
```

### 代码审查清单

```markdown
## 每个PR必须通过

### 代码质量
- [ ] 遵循代码风格（Black, isort）
- [ ] Type hints 完整
- [ ] 函数文档完整（docstring）
- [ ] 错误处理完善
- [ ] 无复杂度过高的函数 (> 10 层嵌套)

### 测试覆盖
- [ ] 新代码有单元测试
- [ ] 边界条件都有测试
- [ ] 错误路径都有测试
- [ ] 覆盖率不下降

### 性能
- [ ] 无明显性能回归
- [ ] 新特性性能达成设计目标
- [ ] 内存使用未增加 > 10%

### 安全
- [ ] 无hardcoded secrets
- [ ] 无 SQL injection 风险
- [ ] 无 XXE/XXS 风险
- [ ] 合理的权限检查

### 文档
- [ ] API 变化有文档更新
- [ ] Breaking changes 明确标记
- [ ] 示例代码正确可运行

### Backward Compatibility
- [ ] 旧API仍可使用
- [ ] 数据结构升级向后兼容
- [ ] 配置文件格式兼容
```

---

## 执行建议

### 1. 团队组织

```
项目经理 (John)
  ├─ 架构审查 (Winston)
  │   └─ 代码审查 (3人轮值)
  │       ├─ Day 1: A审
  │       ├─ Day 2: B审
  │       └─ Day 3: C审
  │
  ├─ 开发队伍
  │   ├─ Agent Parser 实现 (Dev A)
  │   ├─ Context/Generator升级 (Dev B)
  │   └─ 测试/文档 (Dev C)
  │
  └─ QA
      ├─ 单元测试验收
      ├─ 集成测试
      └─ 性能测试

建议: 3-4人，2周冲刺
```

### 2. 风险管理

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| AGENTS.md 格式多样 | 高 | 中 | 使用启发式解析 + 完善测试 |
| 与旧版本冲突 | 中 | 高 | 新建v1_1文件夹，隔离代码 |
| 性能未达目标 | 低 | 中 | Day 3进行性能测试和优化 |
| 文档不完整 | 中 | 低 | Day 3重点投入文档编写 |

### 3. 沟通计划

```
每日站会（上午9:30, 15分钟）:
  - 昨天完成了什么
  - 今天计划做什么
  - 有什么阻碍

每日code review（下午4:00, 30分钟）:
  - 审查当日代码
  - 讨论设计问题
  - 决策critical issues

周五总结（下午3:00, 1小时）:
  - 本周成果回顾
  - 质量指标检查
  - 下周计划调整
```

### 4. 成功度量

```yaml
Day 1:
  目标: Agent Parser 可用 + 单元测试通过
  KPI:
    ✓ 测试通过率 = 100%
    ✓ 覆盖率 >= 85%
    ✓ 无代码审查comments

Day 2:
  目标: 完整的升级 pipeline
  KPI:
    ✓ 集成测试通过 = 100%
    ✓ 性能测试达成 = 100%
    ✓ Backward compatibility = 通过

Day 3:
  目标: v1.1.0-alpha 发布
  KPI:
    ✓ 所有检查清单通过 = 100%
    ✓ 3个真实项目测试通过
    ✓ Release notes 清晰完整
    ✓ 0 critical bugs

v1.1.0 稳定版（Day 6，可选）:
  KPI:
    ✓ Clarity Scorer 集成完成
    ✓ 基础缓存就绪
    ✓ 社区反馈整合
    ✓ 生产监控就位
```

---

## 附录：命令参考

### 开发环境设置

```bash
# 克隆仓库
git clone <repo-url>
cd Prompt-Enhancement

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install pytest pytest-cov black mypy  # dev依赖

# 运行测试
pytest tests/v1_1/ -v
pytest tests/v1_1/ -v --cov=src/v1_1

# 代码格式化
black src/v1_1/
black tests/v1_1/

# 类型检查
mypy src/v1_1/ --strict
```

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/v1.1-brownfield main

# 日常提交
git add src/v1_1/
git commit -m "feat: implement Agent Docs Parser"

# Day 1 完成，合并到 develop
git push origin feature/v1.1-brownfield
# 创建 Pull Request，通过审查后合并到 develop

# Day 3 发布
git checkout main
git merge develop
git tag v1.1.0-alpha
git push origin main --tags
```

### CI/CD 检查清单

```bash
# 本地运行（开发者必须）
pytest tests/ -v
pytest tests/ -v --cov=src >= 80%
black --check src/
mypy src/ --strict

# CI 流水线（自动）
- 单元测试通过
- 集成测试通过
- 代码覆盖率 >= 80%
- Lint 检查无错误
- 文档编译成功
- 性能基准测试通过
```

---

## 总结

本指南按**BMAD brownfield level**清晰地规定了Prompt Enhancement的迭代路径：

| 阶段 | 级别 | 工作量 | 交付物 | 时间 |
|------|------|--------|--------|------|
| **必做** | 2→2.5 | 18-20h | v1.1.0-alpha | Day 1-3 |
| **推荐** | 2.5→3.0 | 15-18h | v1.1.0 | Day 4-6 |
| **长期** | 3→3.5 | 30h+ | v1.2+ | Week 3+ |

**第一个里程碑（Day 3）的关键成果：**
- ✅ Agent Docs Parser 完整可用
- ✅ Context Collector 和 Prompt Generator 升级
- ✅ 完整的文档和示例
- ✅ v1.1.0-alpha 发布就绪

**推荐起始日期**：2025-12-16（明日）

**祝您开发顺利！** 🚀

---

**文档版本**: 1.0
**最后更新**: 2025-12-15
**审核者**: Winston (架构), Mary (分析), Amelia (开发), John (产品)
