# Prompt Enhancement v1.4 - 开发指南

> **版本**: 1.0
> **日期**: 2025-12-24
> **状态**: 基础准备完成

---

## 🚀 快速开始

### 1. 设置PYTHONPATH

```bash
export PYTHONPATH="/path/to/Prompt-Enhancement/src:$PYTHONPATH"
```

或在IDE中配置:
- PyCharm: Settings → Project → Python Interpreter → Add path
- VSCode: 创建 `.env` 文件或修改 `launch.json`

### 2. 验证环境

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement

# 验证版本
python -c "from prompt_enhancement import __version__; print(__version__)"

# 验证v1.2核心模块
python -c "from prompt_enhancement.enhancement.generator import EnhancementGenerator; print('✅ v1.2模块就绪')"
```

### 3. 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_meta/ -v

# 运行带覆盖率
python -m pytest tests/ --cov=src/prompt_enhancement --cov-report=html
```

---

## 📁 v1.4项目结构

```
Prompt-Enhancement/
├── src/prompt_enhancement/
│   ├── meta/                   # ✨ 新增：Meta Prompt Engine
│   │   ├── __init__.py
│   │   ├── prompt_engine.py    # 核心引擎
│   │   └── xml_builder.py      # XML构建工具
│   │
│   ├── improver/               # ✨ 新增：Prompt Improver
│   │   ├── __init__.py
│   │   ├── improver.py         # 核心编排
│   │   ├── strategies/
│   │   │   ├── cot_injection.py
│   │   │   ├── example_standardization.py
│   │   │   ├── example_enrichment.py
│   │   │   ├── instruction_clarity.py
│   │   │   └── variable_tagging.py
│   │   └── feedback_loop.py    # 反馈循环
│   │
│   ├── templates/              # ✨ 新增/扩展：Template Library
│   │   ├── __init__.py
│   │   ├── loader.py           # 模板加载器
│   │   ├── matcher.py          # 模板匹配器
│   │   ├── coding/             # 5个模板
│   │   ├── data/               # 4个模板
│   │   ├── writing/            # 4个模板
│   │   ├── analysis/           # 4个模板
│   │   ├── meta/               # 3个模板
│   │   └── custom/             # 用户模板
│   │
│   ├── workbench/              # ✨ 新增：Workbench系统
│   │   ├── __init__.py
│   │   ├── test_generator.py
│   │   ├── variant_comparator.py
│   │   ├── quality_grader.py
│   │   ├── version_manager.py
│   │   └── export_generator.py
│   │
│   ├── enhancement/            # 现有：增强引擎
│   ├── pipeline/               # 现有：分析管道
│   ├── cli/                    # 现有/扩展：CLI命令
│   ├── config/                 # 现有/扩展：配置
│   ├── cache/                  # 现有：缓存
│   ├── error_handling/         # 现有：错误处理
│   └── ...                     # 其他现有模块
│
├── tests/
│   ├── test_meta/              # ✨ 新增
│   ├── test_improver/          # ✨ 新增
│   ├── test_templates/         # ✨ 新增
│   ├── test_workbench/         # ✨ 新增
│   ├── test_enhancement/       # 现有
│   ├── test_pipeline/          # 现有
│   └── ...                     # 其他现有测试
│
├── docs/
│   ├── v1.4_IMPLEMENTATION_PLAN.md      # 实现计划
│   ├── v1.4_PRD.md                      # 产品需求
│   ├── v1.4_STORIES.md                  # 故事和任务
│   ├── v1.4_WORKFLOW_STATUS.md          # 工作流状态
│   └── v1.4_artifacts/                  # 实现工件
│
└── DEVELOPMENT_v1.4.md          # 本文件

```

---

## 🛠️ 开发工作流

### 1. 启动一个Story

```bash
# 选择要实现的Story
# 例：Epic 1 - Story 1.1 - 变量识别引擎

# 创建对应的module
touch src/prompt_enhancement/meta/prompt_engine.py

# 创建测试文件
touch tests/test_meta/test_prompt_engine.py
```

### 2. 实现Story

**步骤**:
1. 编写测试 (TDD) - 先写失败的测试
2. 编写实现 - 使代码通过测试
3. 重构 - 优化代码质量

**示例代码结构**:

```python
# src/prompt_enhancement/meta/prompt_engine.py

"""MetaPromptEngine - 从任务描述生成XML prompt"""

from typing import List
from dataclasses import dataclass
from prompt_enhancement.enhancement.llm_provider import LLMProvider, create_provider


@dataclass
class Variable:
    """输入变量定义"""
    name: str
    type: str  # code, text, data, etc
    required: bool = True
    description: str = ""


class MetaPromptEngine:
    """从自然语言任务描述生成结构化XML prompt"""

    def __init__(self, llm_provider: LLMProvider):
        self.provider = llm_provider
        self._cache = {}  # 缓存已生成的任务

    def extract_variables(self, task_description: str) -> List[Variable]:
        """
        识别任务描述中需要的变量

        参数:
            task_description: 用户的自然语言任务描述

        返回:
            变量列表
        """
        # 实现逻辑
        pass

    def plan_structure(self, task_description: str, variables: List[Variable]):
        """规划prompt的XML结构"""
        pass

    def write_instructions(self, ...):
        """生成完整的XML prompt"""
        pass
```

### 3. 编写测试

**测试文件结构**:

```python
# tests/test_meta/test_prompt_engine.py

import pytest
from prompt_enhancement.meta.prompt_engine import MetaPromptEngine, Variable


class TestVariableExtraction:
    """测试变量识别"""

    def test_simple_code_task(self):
        """测试简单代码任务的变量识别"""
        engine = MetaPromptEngine()
        task = "帮我写一个代码审查工具"

        variables = engine.extract_variables(task)

        assert len(variables) > 0
        assert any(v.name == "CODE" for v in variables)

    def test_complex_task(self):
        """测试复合任务"""
        engine = MetaPromptEngine()
        task = "生成数据处理和清洗提示词"

        variables = engine.extract_variables(task)

        assert len(variables) >= 2


class TestStructurePlanning:
    """测试结构规划"""

    def test_coding_structure(self):
        """测试代码任务的结构规划"""
        # 实现测试
        pass
```

### 4. 提交变更

```bash
# 查看变更
git status
git diff src/prompt_enhancement/meta/

# 提交
git add src/prompt_enhancement/meta/ tests/test_meta/
git commit -m "feat: implement variable extraction for meta prompt engine

- Implement MetaPromptEngine.extract_variables()
- Add unit tests for simple and complex tasks
- Integrate with existing LLMProvider"

# 推送
git push origin feature/v1.4-brownfield
```

---

## 📊 代码质量标准

### 覆盖率要求

- ✅ 新增代码覆盖率: **>80%**
- ✅ 总体项目覆盖率: **>80%**
- ✅ 关键路径覆盖率: **100%**

### Pylint/代码风格

```bash
# 检查代码风格
pylint src/prompt_enhancement/meta/

# 自动格式化
black src/prompt_enhancement/meta/
isort src/prompt_enhancement/meta/
```

### 类型检查

```bash
# 运行mypy
mypy src/prompt_enhancement/meta/ --ignore-missing-imports
```

---

## 🧪 测试策略

### 单元测试

对每个Story编写单元测试:

```python
# 边界值测试
def test_empty_input(): ...
def test_very_long_input(): ...

# 正常情况测试
def test_simple_task(): ...
def test_complex_task(): ...

# 错误情况测试
def test_invalid_task_description(): ...
def test_api_failure(): ...
```

### 集成测试

跨模块测试:

```python
# tests/test_integration/test_meta_to_cli.py

def test_generate_command_with_meta_engine():
    """测试从CLI生成命令到Meta Engine的完整流程"""
    # 执行 pe generate "任务描述"
    # 验证生成的XML是否有效
    pass
```

### E2E测试

完整工作流测试:

```python
# tests/test_integration/test_v14_workflows.py

def test_complete_workflow():
    """测试完整的v1.4工作流"""
    # 1. 生成prompt
    # 2. 优化prompt
    # 3. 测试prompt
    # 4. 导出prompt
    pass
```

---

## 🔄 关键LLM调用模式

### 使用现有LLMProvider

```python
from prompt_enhancement.enhancement.llm_provider import create_provider

# 创建提供者
provider = create_provider("openai")

# 调用API
response = provider.call(
    system_prompt="你是一个Prompt工程师...",
    user_message="生成一个代码审查prompt...",
    timeout_seconds=30,
    max_tokens=2000
)

print(response.content)  # 生成的内容
print(response.tokens_input)  # 输入token数
print(response.tokens_output)  # 输出token数
```

### 缓存策略

```python
# 为了避免重复调用LLM，使用缓存
class MetaPromptEngine:
    def __init__(self):
        self._cache = {}

    def generate_prompt(self, task_description: str) -> str:
        # 检查缓存
        cache_key = hash(task_description)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 调用LLM
        result = self._call_llm(task_description)

        # 缓存结果
        self._cache[cache_key] = result
        return result
```

---

## 📝 常见问题

### Q: 如何运行特定的Story测试?

```bash
# 运行Story 1.1的测试
pytest tests/test_meta/test_prompt_engine.py::TestVariableExtraction -v
```

### Q: 如何调试LLM调用?

```python
# 在代码中添加日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后运行测试，查看详细日志
pytest tests/test_meta/ -v -s  # -s 显示print输出
```

### Q: 如何查看测试覆盖率?

```bash
# 生成HTML报告
pytest tests/ --cov=src/prompt_enhancement --cov-report=html

# 打开报告
open htmlcov/index.html  # macOS
```

### Q: 如何在多个Python版本上测试?

```bash
# 使用tox
tox -e py38,py39,py310
```

---

## 🎯 检查点

### Before提交代码

- [ ] 所有新增代码有对应测试
- [ ] 测试覆盖率 >80%
- [ ] pylint评分 >8.5
- [ ] 所有v1.2测试仍然通过
- [ ] 代码格式化正确 (black, isort)
- [ ] 类型检查通过 (mypy)
- [ ] 提交信息清晰和完整

### Before完成Story

- [ ] 所有验收标准满足
- [ ] 测试100%通过
- [ ] 文档更新
- [ ] 代码审查通过

### Before完成Epic

- [ ] 所有Stories完成
- [ ] 集成测试通过
- [ ] 性能指标达标
- [ ] 文档完整

---

## 📚 参考资源

- [v1.4 实现规划](./docs/v1.4_IMPLEMENTATION_PLAN.md)
- [v1.4 故事和任务](./docs/v1.4_STORIES.md)
- [v1.2 架构分析](./docs/v1.2_ARCHITECTURE_ANALYSIS.md)
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)

---

**文档结束**
*最后更新: 2025-12-24*
