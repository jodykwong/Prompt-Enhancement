"""
Test suite for symbol_indexer module

测试智能符号提取的四个核心组件：
  1. ExtractedSymbol/FileSymbols - 数据结构
  2. PythonSymbolExtractor - Python AST符号提取
  3. JavaScriptSymbolExtractor - JavaScript正则符号提取
  4. SymbolCache - 智能缓存
  5. SymbolIndexer - 完整流程
"""

import pytest
import sys
import os
import tempfile
import time
from pathlib import Path
from datetime import datetime
import json

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from prompt_enhancement.symbol_indexer import (
    ExtractedSymbol,
    FileSymbols,
    PythonSymbolExtractor,
    JavaScriptSymbolExtractor,
    SymbolCache,
    SymbolIndexer,
)


# ============================================================================
# 测试数据结构
# ============================================================================

class TestExtractedSymbol:
    """测试ExtractedSymbol数据类"""

    def test_create_function_symbol(self):
        """测试创建函数符号"""
        symbol = ExtractedSymbol(
            name="my_func",
            symbol_type="function",
            signature="def my_func(x: int) -> str",
            line_number=10,
        )

        assert symbol.name == "my_func"
        assert symbol.symbol_type == "function"
        assert symbol.line_number == 10
        assert symbol.parent_class is None

    def test_create_class_symbol(self):
        """测试创建类符号"""
        symbol = ExtractedSymbol(
            name="MyClass",
            symbol_type="class",
            signature="class MyClass(Base)",
            line_number=5,
        )

        assert symbol.name == "MyClass"
        assert symbol.symbol_type == "class"
        assert symbol.parent_class is None

    def test_create_method_symbol(self):
        """测试创建方法符号"""
        symbol = ExtractedSymbol(
            name="method",
            symbol_type="method",
            signature="def method(self)",
            line_number=20,
            parent_class="MyClass",
        )

        assert symbol.name == "method"
        assert symbol.parent_class == "MyClass"

    def test_symbol_to_dict(self):
        """测试符号转换为字典"""
        symbol = ExtractedSymbol(
            name="func",
            symbol_type="function",
            signature="def func()",
            line_number=1,
            decorators=["@cached"],
        )

        data = symbol.to_dict()
        assert data['name'] == "func"
        assert data['decorators'] == ["@cached"]


class TestFileSymbols:
    """测试FileSymbols数据类"""

    def test_create_file_symbols(self):
        """测试创建文件符号集合"""
        symbols = [
            ExtractedSymbol("func1", "function", "def func1()", 1),
            ExtractedSymbol("Class1", "class", "class Class1", 10),
        ]

        file_symbols = FileSymbols(
            file_path="/path/to/file.py",
            language="python",
            symbols=symbols,
            extracted_at=datetime.now(),
            file_hash="abc123",
        )

        assert file_symbols.file_path == "/path/to/file.py"
        assert len(file_symbols.symbols) == 2
        assert file_symbols.language == "python"

    def test_file_symbols_serialization(self):
        """测试FileSymbols序列化和反序列化"""
        symbols = [
            ExtractedSymbol("func", "function", "def func()", 1),
        ]

        original = FileSymbols(
            file_path="/test.py",
            language="python",
            symbols=symbols,
            extracted_at=datetime.now(),
            file_hash="hash123",
        )

        # 序列化
        data = original.to_dict()
        assert isinstance(data, dict)

        # 反序列化
        restored = FileSymbols.from_dict(data)
        assert restored.file_path == original.file_path
        assert len(restored.symbols) == len(original.symbols)
        assert restored.symbols[0].name == "func"


# ============================================================================
# Python符号提取器测试
# ============================================================================

class TestPythonSymbolExtractor:
    """测试Python符号提取"""

    @pytest.fixture
    def python_extractor(self):
        """创建Python提取器"""
        return PythonSymbolExtractor()

    @pytest.fixture
    def sample_py_file(self, tmp_path):
        """创建示例Python文件"""
        code = '''
def simple_function():
    """简单函数"""
    pass

def function_with_args(x: int, y: str) -> bool:
    return True

async def async_function(data: dict):
    """异步函数"""
    pass

@cached
def decorated_function():
    pass

class MyClass:
    """示例类"""

    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    async def async_method(self):
        pass

class ChildClass(MyClass):
    """继承类"""
    pass
'''
        file_path = tmp_path / "sample.py"
        file_path.write_text(code)
        return file_path

    def test_extract_simple_function(self, python_extractor, sample_py_file):
        """测试提取简单函数"""
        symbols = python_extractor.extract(str(sample_py_file))

        # 查找simple_function
        simple = next((s for s in symbols if s.name == "simple_function"), None)
        assert simple is not None
        assert simple.symbol_type == "function"
        assert "simple_function" in simple.signature

    def test_extract_function_with_type_hints(self, python_extractor, sample_py_file):
        """测试提取带类型注解的函数"""
        symbols = python_extractor.extract(str(sample_py_file))

        func = next((s for s in symbols if s.name == "function_with_args"), None)
        assert func is not None
        assert "int" in func.signature
        assert "str" in func.signature
        assert "bool" in func.signature

    def test_extract_async_function(self, python_extractor, sample_py_file):
        """测试提取异步函数"""
        symbols = python_extractor.extract(str(sample_py_file))

        async_func = next((s for s in symbols if s.name == "async_function"), None)
        assert async_func is not None
        assert async_func.symbol_type == "async_function"
        assert "async" in async_func.signature

    def test_extract_decorated_function(self, python_extractor, sample_py_file):
        """测试提取装饰器函数"""
        symbols = python_extractor.extract(str(sample_py_file))

        decorated = next((s for s in symbols if s.name == "decorated_function"), None)
        assert decorated is not None
        assert len(decorated.decorators) > 0
        assert "cached" in decorated.decorators

    def test_extract_class(self, python_extractor, sample_py_file):
        """测试提取类定义"""
        symbols = python_extractor.extract(str(sample_py_file))

        my_class = next((s for s in symbols if s.name == "MyClass"), None)
        assert my_class is not None
        assert my_class.symbol_type == "class"

    def test_extract_class_with_methods(self, python_extractor, sample_py_file):
        """测试提取类的方法"""
        symbols = python_extractor.extract(str(sample_py_file))

        # 查找__init__方法
        init = next((s for s in symbols if s.name == "__init__" and s.parent_class == "MyClass"), None)
        assert init is not None
        assert init.symbol_type == "method"
        assert init.parent_class == "MyClass"

        # 查找get_name方法
        get_name = next((s for s in symbols if s.name == "get_name"), None)
        assert get_name is not None
        assert get_name.parent_class == "MyClass"

    def test_extract_class_inheritance(self, python_extractor, sample_py_file):
        """测试提取继承类"""
        symbols = python_extractor.extract(str(sample_py_file))

        child = next((s for s in symbols if s.name == "ChildClass"), None)
        assert child is not None
        assert "MyClass" in child.signature

    def test_extract_docstrings(self, python_extractor, sample_py_file):
        """测试提取文档字符串"""
        symbols = python_extractor.extract(str(sample_py_file))

        my_class = next((s for s in symbols if s.name == "MyClass"), None)
        assert my_class is not None
        assert my_class.docstring is not None
        assert "示例类" in my_class.docstring

    def test_extract_empty_file(self, python_extractor, tmp_path):
        """测试提取空文件"""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        symbols = python_extractor.extract(str(empty_file))
        assert symbols == []

    def test_extract_syntax_error_file(self, python_extractor, tmp_path):
        """测试提取有语法错误的文件"""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(:\n    pass")

        symbols = python_extractor.extract(str(bad_file))
        assert symbols == []


# ============================================================================
# JavaScript符号提取器测试
# ============================================================================

class TestJavaScriptSymbolExtractor:
    """测试JavaScript符号提取"""

    @pytest.fixture
    def js_extractor(self):
        """创建JavaScript提取器"""
        return JavaScriptSymbolExtractor()

    @pytest.fixture
    def sample_js_file(self, tmp_path):
        """创建示例JavaScript文件"""
        code = '''
function simpleFunction() {
    return "hello";
}

function functionWithArgs(x, y) {
    return x + y;
}

const arrowFunc = (a, b) => a * b;

class MyClass {
    constructor(name) {
        this.name = name;
    }

    getName() {
        return this.name;
    }
}

class ChildClass extends MyClass {
    constructor(name, age) {
        super(name);
        this.age = age;
    }
}
'''
        file_path = tmp_path / "sample.js"
        file_path.write_text(code)
        return file_path

    def test_extract_function_declaration(self, js_extractor, sample_js_file):
        """测试提取函数声明"""
        symbols = js_extractor.extract(str(sample_js_file))

        simple = next((s for s in symbols if s.name == "simpleFunction"), None)
        assert simple is not None
        assert simple.symbol_type == "function"

    def test_extract_function_with_args(self, js_extractor, sample_js_file):
        """测试提取带参数的函数"""
        symbols = js_extractor.extract(str(sample_js_file))

        func = next((s for s in symbols if s.name == "functionWithArgs"), None)
        assert func is not None
        assert "x" in func.signature
        assert "y" in func.signature

    def test_extract_arrow_function(self, js_extractor, sample_js_file):
        """测试提取箭头函数"""
        symbols = js_extractor.extract(str(sample_js_file))

        arrow = next((s for s in symbols if s.name == "arrowFunc"), None)
        assert arrow is not None
        assert arrow.symbol_type == "function"
        assert "=>" in arrow.signature

    def test_extract_class(self, js_extractor, sample_js_file):
        """测试提取类定义"""
        symbols = js_extractor.extract(str(sample_js_file))

        my_class = next((s for s in symbols if s.name == "MyClass"), None)
        assert my_class is not None
        assert my_class.symbol_type == "class"

    def test_extract_class_inheritance(self, js_extractor, sample_js_file):
        """测试提取继承类"""
        symbols = js_extractor.extract(str(sample_js_file))

        child = next((s for s in symbols if s.name == "ChildClass"), None)
        assert child is not None
        assert "extends MyClass" in child.signature

    def test_extract_class_methods(self, js_extractor, sample_js_file):
        """测试提取类方法"""
        symbols = js_extractor.extract(str(sample_js_file))

        # 查找constructor
        constructor = next((s for s in symbols if s.name == "constructor" and s.parent_class == "MyClass"), None)
        assert constructor is not None
        assert constructor.symbol_type == "method"

        # 查找getName
        get_name = next((s for s in symbols if s.name == "getName"), None)
        assert get_name is not None
        assert get_name.parent_class == "MyClass"

    def test_extract_empty_file(self, js_extractor, tmp_path):
        """测试提取空文件"""
        empty_file = tmp_path / "empty.js"
        empty_file.write_text("")

        symbols = js_extractor.extract(str(empty_file))
        assert symbols == []


# ============================================================================
# 符号缓存测试
# ============================================================================

class TestSymbolCache:
    """测试符号缓存"""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """创建临时缓存目录"""
        cache_dir = tmp_path / "cache"
        return str(cache_dir)

    def test_cache_initialization(self, temp_cache_dir):
        """测试缓存初始化"""
        cache = SymbolCache(cache_dir=temp_cache_dir)
        assert Path(temp_cache_dir).exists()

    def test_cache_miss(self, temp_cache_dir):
        """测试缓存未命中"""
        cache = SymbolCache(cache_dir=temp_cache_dir)
        result = cache.get("/nonexistent/file.py")
        assert result is None

    def test_cache_set_and_get(self, temp_cache_dir, tmp_path):
        """测试缓存保存和获取"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        # 创建符号
        symbols = [ExtractedSymbol("test", "function", "def test()", 1)]
        file_symbols = FileSymbols(
            file_path=str(test_file),
            language="python",
            symbols=symbols,
            extracted_at=datetime.now(),
            file_hash=SymbolCache(cache_dir=temp_cache_dir)._compute_file_hash(str(test_file)),
        )

        # 保存到缓存
        cache = SymbolCache(cache_dir=temp_cache_dir)
        cache.set(str(test_file), file_symbols)

        # 从缓存获取
        retrieved = cache.get(str(test_file))
        assert retrieved is not None
        assert retrieved.file_path == str(test_file)
        assert len(retrieved.symbols) == 1
        assert retrieved.symbols[0].name == "test"

    def test_cache_invalidation_on_file_change(self, temp_cache_dir, tmp_path):
        """测试文件修改时缓存失效"""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        cache = SymbolCache(cache_dir=temp_cache_dir)
        original_hash = cache._compute_file_hash(str(test_file))

        # 创建缓存
        symbols = [ExtractedSymbol("test", "function", "def test()", 1)]
        file_symbols = FileSymbols(
            file_path=str(test_file),
            language="python",
            symbols=symbols,
            extracted_at=datetime.now(),
            file_hash=original_hash,
        )
        cache.set(str(test_file), file_symbols)

        # 修改文件
        test_file.write_text("def test2(): pass")

        # 缓存应该失效
        retrieved = cache.get(str(test_file))
        assert retrieved is None

    def test_clear_stale_cache(self, temp_cache_dir, tmp_path):
        """测试清理过时缓存"""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        cache = SymbolCache(cache_dir=temp_cache_dir)

        # 创建缓存
        symbols = [ExtractedSymbol("test", "function", "def test()", 1)]
        file_symbols = FileSymbols(
            file_path=str(test_file),
            language="python",
            symbols=symbols,
            extracted_at=datetime.now(),
            file_hash=cache._compute_file_hash(str(test_file)),
        )
        cache.set(str(test_file), file_symbols)

        # 删除文件
        test_file.unlink()

        # 清理过时缓存
        cache.clear_stale()
        assert str(test_file) not in cache._memory_cache


# ============================================================================
# 符号索引器测试
# ============================================================================

class TestSymbolIndexer:
    """测试符号索引器（端到端）"""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """创建临时缓存目录"""
        return str(tmp_path / "cache")

    def test_index_python_file(self, tmp_path, temp_cache_dir):
        """测试索引Python文件"""
        py_file = tmp_path / "test.py"
        py_file.write_text("""
def hello():
    pass

class MyClass:
    def method(self):
        pass
""")

        indexer = SymbolIndexer(str(tmp_path), use_cache=False)
        file_symbols = indexer.index_file(str(py_file))

        assert file_symbols.language == "python"
        assert len(file_symbols.symbols) > 0
        assert any(s.name == "hello" for s in file_symbols.symbols)
        assert any(s.name == "MyClass" for s in file_symbols.symbols)

    def test_index_javascript_file(self, tmp_path, temp_cache_dir):
        """测试索引JavaScript文件"""
        js_file = tmp_path / "test.js"
        js_file.write_text("""
function greet() {
    return "hello";
}

class Greeter {
    greet() {
        return "hi";
    }
}
""")

        indexer = SymbolIndexer(str(tmp_path), use_cache=False)
        file_symbols = indexer.index_file(str(js_file))

        assert file_symbols.language == "javascript"
        assert len(file_symbols.symbols) > 0

    def test_batch_index(self, tmp_path):
        """测试批量索引"""
        # 创建多个文件
        py_file = tmp_path / "test.py"
        py_file.write_text("def test(): pass")

        js_file = tmp_path / "test.js"
        js_file.write_text("function test() {}")

        indexer = SymbolIndexer(str(tmp_path), use_cache=False)
        results = indexer.index_files([str(py_file), str(js_file)])

        assert len(results) == 2
        assert str(py_file) in results
        assert str(js_file) in results

    def test_cache_performance(self, tmp_path, temp_cache_dir):
        """测试缓存性能"""
        py_file = tmp_path / "test.py"
        py_file.write_text("def test(): pass")

        indexer = SymbolIndexer(str(tmp_path), use_cache=True)

        # 第一次索引（无缓存）
        start = time.time()
        result1 = indexer.index_file(str(py_file))
        first_time = time.time() - start

        # 第二次索引（有缓存）
        start = time.time()
        result2 = indexer.index_file(str(py_file))
        second_time = time.time() - start

        # 缓存应该更快
        assert result1 == result2
        # 注意：在测试环境中可能无法可靠地测试时间
        # 但我们可以至少验证结果相同

    def test_get_file_symbols(self, tmp_path):
        """测试高层API get_file_symbols"""
        py_file = tmp_path / "test.py"
        py_file.write_text("""
def func1():
    pass

def func2(x):
    pass
""")

        indexer = SymbolIndexer(str(tmp_path))
        symbols = indexer.get_file_symbols(str(py_file))

        assert len(symbols) > 0
        assert any(s.name == "func1" for s in symbols)
        assert any(s.name == "func2" for s in symbols)


# ============================================================================
# 集成测试
# ============================================================================

class TestIntegration:
    """集成测试"""

    def test_full_workflow(self, tmp_path):
        """测试完整工作流"""
        # 创建示例Python文件
        py_file = tmp_path / "example.py"
        py_file.write_text("""
class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        return [x * 2 for x in self.data]

    async def async_process(self):
        return await self._do_process()

    def _do_process(self):
        pass

def utility_function(a, b):
    return a + b
""")

        # 创建索引器并索引文件
        indexer = SymbolIndexer(str(tmp_path))
        file_symbols = indexer.index_file(str(py_file))

        # 验证结果
        assert file_symbols.language == "python"
        assert len(file_symbols.symbols) >= 5  # 至少包含类、构造函数、3个方法和1个函数

        # 验证特定符号
        symbols_by_name = {s.name: s for s in file_symbols.symbols}

        assert "DataProcessor" in symbols_by_name
        assert symbols_by_name["DataProcessor"].symbol_type == "class"

        assert "__init__" in symbols_by_name
        assert symbols_by_name["__init__"].parent_class == "DataProcessor"

        assert "utility_function" in symbols_by_name
        assert symbols_by_name["utility_function"].symbol_type == "function"
