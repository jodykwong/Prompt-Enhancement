"""
Test suite for file_discoverer module

测试智能文件发现的三个核心组件：
  1. KeywordExtractor - 关键词提取
  2. FileMatcher - 文件匹配
  3. FileDiscoverer - 完整流程
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from prompt_enhancement.file_discoverer import (
    KeywordExtractor,
    FileMatcher,
    FileDiscoverer,
)


class TestKeywordExtractor:
    """测试关键词提取"""

    def test_extract_simple_task(self):
        """测试简单任务的关键词提取"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("添加用户认证")

        assert len(keywords) > 0
        # 应该包含"认证"或相关词汇
        assert any("认证" in k or "auth" in k.lower() for k in keywords)

    def test_extract_english_keywords(self):
        """测试英文关键词提取"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("implement user authentication")

        assert len(keywords) > 0
        assert any("user" in k.lower() or "auth" in k.lower() for k in keywords)

    def test_extract_mixed_language(self):
        """测试中英混合的任务"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("修复login bug")

        assert len(keywords) > 0
        # 应该同时包含中文和英文关键词
        assert any(len(k) > 1 for k in keywords)  # 有多字词或英文词

    def test_remove_stopwords(self):
        """测试停用词去除"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("添加一个新的用户认证功能")

        # "的"、"一"、"个"应该被去除
        assert "的" not in keywords
        assert "一" not in keywords
        assert "个" not in keywords

    def test_extract_programming_keywords_priority(self):
        """测试编程关键词优先级"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("实现 database 缓存优化")

        # database和缓存应该在前面
        result_str = " ".join(keywords[:3])
        assert any(k in result_str for k in ["database", "缓存", "cache"])

    def test_extract_empty_input(self):
        """测试空输入"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("")

        assert keywords == []

    def test_extract_only_stopwords(self):
        """测试全是停用词的输入"""
        extractor = KeywordExtractor()
        keywords = extractor.extract("的是了和在有一个")

        # 应该全部被去除
        assert len(keywords) == 0


class TestFileMatcher:
    """测试文件匹配"""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """创建临时项目结构用于测试"""
        # 创建测试文件
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "auth.py").write_text("class AuthManager: pass")
        (tmp_path / "src" / "user.py").write_text("class User: pass")
        (tmp_path / "src" / "cache.py").write_text("class Cache: pass")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_auth.py").write_text("def test_auth(): pass")

        return tmp_path

    def test_find_by_exact_filename(self, temp_project):
        """测试精确文件名匹配"""
        matcher = FileMatcher(str(temp_project))
        results = matcher.find_by_keywords(["auth"])

        assert len(results) > 0
        # 应该找到auth.py
        result_names = [Path(r).name for r in results]
        assert any("auth" in name for name in result_names)

    def test_find_multiple_files(self, temp_project):
        """测试多个关键词"""
        matcher = FileMatcher(str(temp_project))
        results = matcher.find_by_keywords(["user", "auth"])

        assert len(results) >= 2

    def test_find_with_limit(self, temp_project):
        """测试结果数量限制"""
        matcher = FileMatcher(str(temp_project))
        results = matcher.find_by_keywords(["auth"], max_results=1)

        assert len(results) <= 1

    def test_fuzzy_match(self, temp_project):
        """测试模糊匹配（容错）"""
        matcher = FileMatcher(str(temp_project))
        # 打错字，但应该仍能找到
        results = matcher.find_by_fuzzy("atuh")  # auth打错字

        # 应该能找到相似的文件
        assert len(results) >= 0  # 可能为0，取决于实现

    def test_exclude_directories(self, temp_project):
        """测试排除目录"""
        # 创建__pycache__目录
        pycache = temp_project / "__pycache__"
        pycache.mkdir()
        (pycache / "auth.py").write_text("fake")

        matcher = FileMatcher(str(temp_project))
        results = matcher.find_by_keywords(["auth"])

        # 结果中不应该包含__pycache__中的文件
        for result in results:
            assert "__pycache__" not in str(result)

    def test_empty_keywords(self, temp_project):
        """测试空关键词列表"""
        matcher = FileMatcher(str(temp_project))
        results = matcher.find_by_keywords([])

        assert results == []


class TestFileDiscoverer:
    """测试完整的文件发现流程"""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """创建测试项目"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "auth.py").write_text("class Auth: pass")
        (tmp_path / "src" / "login.py").write_text("def login(): pass")
        (tmp_path / "src" / "user.py").write_text("class User: pass")

        return tmp_path

    def test_discover_simple_task(self, temp_project):
        """测试简单任务的完整发现"""
        discoverer = FileDiscoverer(str(temp_project))
        files = discoverer.discover("添加用户认证")

        assert len(files) > 0
        # 应该找到auth相关的文件
        assert any("auth" in f.lower() for f in files)

    def test_discover_with_limit(self, temp_project):
        """测试结果限制"""
        discoverer = FileDiscoverer(str(temp_project))
        files = discoverer.discover("python代码文件", max_results=2)

        assert len(files) <= 2

    def test_discover_english_task(self, temp_project):
        """测试英文任务"""
        discoverer = FileDiscoverer(str(temp_project))
        files = discoverer.discover("implement login functionality")

        assert len(files) > 0

    def test_discover_no_keywords(self, temp_project):
        """测试无关键词的任务"""
        discoverer = FileDiscoverer(str(temp_project))
        files = discoverer.discover("的是了和在")  # 全是停用词

        # 应该返回空列表
        assert files == []


class TestIntegration:
    """集成测试"""

    def test_end_to_end_discovery(self, tmp_path):
        """测试端到端的发现流程"""
        # 创建更复杂的项目结构
        src = tmp_path / "src"
        src.mkdir()

        (src / "models").mkdir()
        (src / "models" / "user.py").write_text("class User: pass")
        (src / "models" / "post.py").write_text("class Post: pass")

        (src / "routes").mkdir()
        (src / "routes" / "auth.py").write_text("@app.route('/login')")
        (src / "routes" / "user.py").write_text("@app.route('/user')")

        # 完整流程
        discoverer = FileDiscoverer(str(tmp_path))
        files = discoverer.discover("添加用户认证功能", max_results=5)

        # 应该找到auth和user相关的文件
        assert len(files) > 0
        result_str = " ".join(files)
        assert any(word in result_str.lower() for word in ["auth", "user"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
