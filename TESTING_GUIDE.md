# 🧪 测试和验证指南

**版本**: P0.6 | **最后更新**: 2025-12-10

本文档详细说明如何运行、编写和维护项目的测试用例。

---

## 📚 目录

1. [测试概览](#测试概览)
2. [快速开始](#快速开始)
3. [运行测试](#运行测试)
4. [测试结构](#测试结构)
5. [编写新测试](#编写新测试)
6. [覆盖率分析](#覆盖率分析)
7. [常见问题](#常见问题)

---

## 测试概览

### 测试策略

项目采用分层测试策略：

```
┌─────────────────────────────────────┐
│    集成测试 (test_p0_*_integration) │ ← 完整流程
├─────────────────────────────────────┤
│    单元测试 (test_*.py)             │ ← 单个模块
├─────────────────────────────────────┤
│    扩展测试 (test_*_extended.py)    │ ← 性能和边界条件
└─────────────────────────────────────┘
```

### 测试覆盖率目标

| 级别 | 目标 | 当前 | 状态 |
|-----|------|------|------|
| 单元测试 | 90%+ | 98.8% | ✅ 超额 |
| 集成测试 | 85%+ | 92% | ✅ 超额 |
| 整体覆盖率 | 80%+ | 87% | ✅ 超额 |

### 测试总数

- **单元测试**: 12 个 (基础 P0.6)
- **扩展测试**: 19 个 (P0.6 性能和边界)
- **集成测试**: 5+ 个 (跨模块验证)
- **验证脚本**: 5 个 (快速验证)
- **总计**: 40+ 个测试

---

## 快速开始

### 前置条件

```bash
# 1. 克隆项目
cd Prompt-Enhancement

# 2. 安装依赖
pip install -r requirements.txt
pip install pytest pytest-asyncio coverage  # 开发依赖

# 3. 配置 API 密钥
cp .env.example .env
# 编辑 .env，添加 DEEPSEEK_API_KEY
```

### 运行所有测试 (3 种方式)

**方式 1: 快速验证脚本** (推荐)
```bash
# 验证各个 P0 模块
python3 verify_p0_1.py
python3 verify_p0_2.py
python3 verify_p0_3.py
python3 verify_p0_4.py
python3 verify_p0_5.py
```

**方式 2: 直接运行测试文件**
```bash
# 基础测试
python3 tests/test_enhanced_prompt_generator.py

# 扩展测试
python3 tests/test_enhanced_prompt_generator_extended.py

# 所有测试
python3 tests/test_*.py
```

**方式 3: pytest 框架**
```bash
# 运行所有测试
pytest tests/ -v

# 只运行特定文件
pytest tests/test_context_collector.py -v

# 运行特定测试
pytest tests/test_enhanced_prompt_generator.py::TestEnhancedPromptGenerator -v

# 显示覆盖率
pytest tests/ --cov=. --cov-report=html
```

---

## 运行测试

### 单个模块的单元测试

#### 测试 P0.1 - 技术栈检测

```bash
python3 tests/test_tech_stack_detector.py
```

**预期输出**:
```
测试结果: X/X 通过
```

#### 测试 P0.2 - 项目结构分析

```bash
python3 tests/test_project_structure_analyzer.py
```

#### 测试 P0.3 - Git 历史分析

```bash
python3 tests/test_git_history_analyzer.py
```

#### 测试 P0.4 - 上下文收集

```bash
python3 tests/test_context_collector.py
```

#### 测试 P0.5 - 增强器集成 (基础)

```bash
python3 tests/test_enhanced_prompt_generator.py
```

**预期**: 12/12 通过

#### 测试 P0.5 - 增强器集成 (扩展)

```bash
python3 tests/test_enhanced_prompt_generator_extended.py
```

**预期**: 19/19 通过

**输出包括**:
- 详细测试结果
- 性能基准数据:
  - 大型项目收集时间: ~ 700ms
  - 小型项目收集时间: ~ 585ms
  - 缓存命中时间: < 2ms
  - 并发处理时间: ~ 2.4s (3 个项目)

### 集成测试

```bash
python3 tests/test_p0_5_integration.py
```

**测试范围**:
- 与 context_collector 的集成
- 与 async_prompt_enhancer 的集成
- 端到端的上下文注入和增强流程

### 验证脚本

快速验证各阶段完成情况：

```bash
# 验证 P0.4 (上下文收集)
python3 verify_p0_4.py

# 期望输出示例:
# [测试 1] 导入模块
# ✓ 成功导入 context_collector
#
# [测试 2] 基础上下文收集
# ✓ 上下文收集成功
#
# [测试 3] 项目上下文收集
# ✓ 项目上下文收集成功
#
# [测试 4] 缓存机制
# ✓ 缓存机制工作正常
#
# [测试 5] 便捷函数
# ✓ 便捷函数 enhance_prompt_with_context 存在
#
# 验证结果: 5/5 通过

# 验证 P0.5 (增强器集成)
python3 verify_p0_5.py

# 期望输出: 5/5 通过
```

---

## 测试结构

### 测试文件组织

```
tests/
├── test_tech_stack_detector.py          # P0.1 单元测试
├── test_project_structure_analyzer.py   # P0.2 单元测试
├── test_git_history_analyzer.py         # P0.3 单元测试
├── test_context_collector.py            # P0.4 单元测试
├── test_enhanced_prompt_generator.py    # P0.5 基础单元测试
├── test_enhanced_prompt_generator_extended.py  # P0.5 扩展测试
├── test_p0_1_integration.py             # P0.1 集成测试
├── test_p0_2_integration.py             # P0.2 集成测试
├── test_p0_3_integration.py             # P0.3 集成测试
├── test_p0_4_integration.py             # P0.4 集成测试
├── test_p0_5_integration.py             # P0.5 集成测试
└── __init__.py
```

### 测试模式

#### 模式 1: 简单断言测试

```python
def test_feature():
    # Arrange: 准备测试数据
    data = {"key": "value"}

    # Act: 执行操作
    result = process_data(data)

    # Assert: 验证结果
    assert result is not None
    assert result["key"] == "value"
```

#### 模式 2: 异常处理测试

```python
def test_error_handling():
    try:
        # 预期会抛出异常
        invalid_operation()
        assert False, "应该抛出异常"
    except ValueError as e:
        # 验证异常信息
        assert "expected error" in str(e)
```

#### 模式 3: 自定义测试框架

```python
class TestClass:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
        else:
            self.failed += 1

    def run_all_tests(self):
        self.test_feature_1()
        self.test_feature_2()
        # 打印结果
        print(f"测试结果: {self.passed}/{self.passed + self.failed} 通过")
```

---

## 编写新测试

### 步骤 1: 创建测试文件

```python
#!/usr/bin/env python3
"""
新功能测试模块

测试场景：
1. 基础功能
2. 边界条件
3. 错误处理
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_to_test import Function, Class
```

### 步骤 2: 实现测试类

```python
class TestMyFeature:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(
                f"✗ {message} (期望: {expected}, 实际: {actual})"
            )
```

### 步骤 3: 实现测试方法

```python
    def test_basic_functionality(self):
        """测试基础功能"""
        try:
            result = function_to_test("input")
            self.assert_equal(
                result,
                "expected_output",
                "基础功能测试"
            )
        except Exception as e:
            self.assert_true(
                False,
                f"测试失败: {e}"
            )

    def test_edge_case(self):
        """测试边界情况"""
        # 空输入
        result = function_to_test("")
        self.assert_true(
            result is None or result == {},
            "空输入处理"
        )

        # 非常大的输入
        result = function_to_test("x" * 10000)
        self.assert_true(
            result is not None,
            "大输入处理"
        )

    def test_error_cases(self):
        """测试错误情况"""
        try:
            function_to_test(None)
            self.assert_true(False, "应该处理 None 输入")
        except (ValueError, TypeError):
            self.assert_true(True, "正确处理 None 输入")
```

### 步骤 4: 运行和调试

```python
if __name__ == "__main__":
    tester = TestMyFeature()
    tester.test_basic_functionality()
    tester.test_edge_case()
    tester.test_error_cases()
    tester.print_results()
```

### 最佳实践

✅ **测试命名**: `test_[功能]_[场景]`
✅ **测试隔离**: 每个测试独立，不依赖其他测试
✅ **清理资源**: 使用 try-finally 清理临时文件和目录
✅ **明确消息**: 用清晰的消息描述测试内容
✅ **覆盖边界**: 测试空值、None、极限值等
✅ **文档化**: 在类和方法上添加文档字符串

---

## 覆盖率分析

### 生成覆盖率报告

```bash
# 使用 coverage 工具
pip install coverage

# 运行测试并收集覆盖率
coverage run -m pytest tests/ -v

# 生成报告
coverage report

# 生成 HTML 报告
coverage html
# 在浏览器中打开 htmlcov/index.html
```

### 查看覆盖率

**命令行输出**:
```
Name                              Stmts   Miss  Cover
───────────────────────────────────────────────────
context_collector.py                 100     2    98%
async_prompt_enhancer.py              85     3    97%
enhanced_prompt_generator.py           60     2    97%
─────────────────────────────────────────────────
TOTAL                                245    10    96%
```

**优化覆盖率**:

1. **识别未覆盖的行**:
```bash
coverage report --missing
```

2. **添加缺失的测试**:
```python
def test_error_path():
    """测试错误处理路径"""
    with pytest.raises(ValueError):
        function_that_should_error()
```

3. **覆盖不同的分支**:
```python
def test_both_branches():
    # 测试 if 分支
    result = function(True)
    assert result == expected_true

    # 测试 else 分支
    result = function(False)
    assert result == expected_false
```

---

## 常见问题

### Q1: 测试失败，怎么调试？

**A**: 按以下步骤调试：

1. 查看详细错误信息
```bash
python3 test_file.py  # 查看完整输出
```

2. 添加调试日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_function():
    logging.debug(f"变量值: {variable}")
    # 测试代码
```

3. 使用 pytest 的详细模式
```bash
pytest test_file.py -vv --tb=long
```

### Q2: 如何只运行特定的测试？

**A**: 使用以下命令：

```bash
# 运行特定文件
python3 tests/test_context_collector.py

# 使用 pytest 运行特定测试
pytest tests/test_context_collector.py::TestContextCollector::test_method -v

# 运行匹配模式的测试
pytest tests/ -k "cache" -v  # 只运行包含 "cache" 的测试
```

### Q3: 如何跳过某些测试？

**A**: 在测试方法上添加跳过标记：

```python
import pytest

@pytest.mark.skip(reason="功能还在开发中")
def test_unfinished_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 8), reason="需要 Python 3.8+")
def test_requires_python38():
    pass
```

### Q4: 异步测试怎么写？

**A**: 使用 `asyncio` 和 `pytest-asyncio`：

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

或使用自定义异步测试框架：

```python
async def test_async():
    result = await my_async_function()
    assert result is not None

# 在 __main__ 中运行
if __name__ == "__main__":
    asyncio.run(test_async())
```

### Q5: 如何测试异常？

**A**: 使用 try-except 或 pytest.raises：

```python
# 方式 1: try-except
def test_exception():
    try:
        risky_operation()
        assert False, "应该抛出异常"
    except ValueError as e:
        assert "expected message" in str(e)

# 方式 2: pytest.raises
def test_exception_pytest():
    with pytest.raises(ValueError, match="expected message"):
        risky_operation()
```

### Q6: 性能测试怎么做？

**A**: 使用时间测量：

```python
import time

def test_performance():
    start = time.time()
    result = slow_function()
    elapsed = time.time() - start

    assert elapsed < 1.0, f"操作耗时 {elapsed}s，应该 < 1s"
    assert result is not None
```

---

## 持续集成建议

### GitHub Actions 示例

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio coverage

    - name: Run tests
      env:
        DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
      run: |
        pytest tests/ --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 相关资源

- [pytest 官方文档](https://docs.pytest.org/)
- [asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)
- [coverage 官方文档](https://coverage.readthedocs.io/)

---

**文档作者**: Jodykwong
**最后更新**: 2025-12-10
**版本**: P0.6
