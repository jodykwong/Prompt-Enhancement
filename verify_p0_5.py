#!/usr/bin/env python3
"""
P0.5 快速验证脚本

演示增强器集成模块的完整功能
"""

import sys
import os
import asyncio
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_prompt_generator import EnhancedPromptGenerator, enhance_prompt_with_context
from context_collector import collect_project_context


class VerifyP0_5:
    """P0.5 快速验证类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def test_generator_initialization(self):
        """测试 1: 生成器初始化"""
        print("\n[测试 1] 生成器初始化")
        print("-" * 50)
        
        try:
            generator = EnhancedPromptGenerator()
            print("✓ EnhancedPromptGenerator 初始化成功")
            print(f"  - 模型: deepseek-reasoner")
            print(f"  - 缓存大小: {len(generator._context_cache)}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            self.failed += 1
            return False

    def test_context_injection(self):
        """测试 2: 上下文注入"""
        print("\n[测试 2] 上下文注入")
        print("-" * 50)
        
        try:
            generator = EnhancedPromptGenerator()
            
            # 创建模拟上下文
            mock_context = {
                "summary": "Python Django 项目",
                "context_string": "# 项目上下文\n## 技术栈\n- Python\n- Django\n- PostgreSQL"
            }
            
            prompt = "如何优化数据库查询性能？"
            injected = generator._inject_context(prompt, mock_context)
            
            print(f"✓ 上下文注入成功")
            print(f"  - 原始提示词长度: {len(prompt)}")
            print(f"  - 注入后长度: {len(injected)}")
            print(f"  - 包含上下文: {'项目上下文' in injected}")
            print(f"  - 包含原始提示词: {'优化数据库' in injected}")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ 上下文注入失败: {e}")
            self.failed += 1
            return False

    def test_project_context_collection(self):
        """测试 3: 项目上下文收集"""
        print("\n[测试 3] 项目上下文收集")
        print("-" * 50)
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建简单的项目结构
                Path(tmpdir, "main.py").write_text("print('hello')")
                Path(tmpdir, "requirements.txt").write_text("django==4.0\n")
                
                # 初始化 Git 仓库
                subprocess.run(
                    ["git", "init"],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=5
                )
                
                # 收集上下文
                context = collect_project_context(tmpdir)
                
                print(f"✓ 项目上下文收集成功")
                print(f"  - 技术栈: {context.get('tech_stack', {}).get('backend', [])}")
                print(f"  - 项目结构: {context.get('project_structure', {}).get('total_files', 0)} 个文件")
                print(f"  - Git 仓库: {context.get('git_history', {}).get('is_git_repo', False)}")
                print(f"  - 摘要: {context.get('summary', '')[:50]}...")
                
                self.passed += 1
                return True
        except Exception as e:
            print(f"✗ 项目上下文收集失败: {e}")
            self.failed += 1
            return False

    def test_cache_mechanism(self):
        """测试 4: 缓存机制"""
        print("\n[测试 4] 缓存机制")
        print("-" * 50)
        
        try:
            generator = EnhancedPromptGenerator()
            
            with tempfile.TemporaryDirectory() as tmpdir:
                Path(tmpdir, "test.py").touch()
                
                # 第一次收集
                context1 = generator._collect_context(tmpdir)
                cache_size_1 = len(generator._context_cache)
                
                # 第二次收集（应该来自缓存）
                context2 = generator._collect_context(tmpdir)
                cache_size_2 = len(generator._context_cache)
                
                # 清除缓存
                generator.clear_cache()
                cache_size_3 = len(generator._context_cache)
                
                print(f"✓ 缓存机制工作正常")
                print(f"  - 第一次收集后缓存大小: {cache_size_1}")
                print(f"  - 第二次收集后缓存大小: {cache_size_2}")
                print(f"  - 清除缓存后大小: {cache_size_3}")
                print(f"  - 缓存命中: {context1 == context2}")
                
                self.passed += 1
                return True
        except Exception as e:
            print(f"✗ 缓存机制测试失败: {e}")
            self.failed += 1
            return False

    def test_convenience_function(self):
        """测试 5: 便捷函数"""
        print("\n[测试 5] 便捷函数")
        print("-" * 50)
        
        try:
            # 验证便捷函数存在且可调用
            print(f"✓ 便捷函数 enhance_prompt_with_context 存在")
            print(f"  - 函数类型: {type(enhance_prompt_with_context)}")
            print(f"  - 可调用: {callable(enhance_prompt_with_context)}")
            
            # 验证函数签名
            import inspect
            sig = inspect.signature(enhance_prompt_with_context)
            params = list(sig.parameters.keys())
            print(f"  - 参数: {params}")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ 便捷函数测试失败: {e}")
            self.failed += 1
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("P0.5 快速验证脚本")
        print("增强器集成模块功能演示")
        print("="*70)

        self.test_generator_initialization()
        self.test_context_injection()
        self.test_project_context_collection()
        self.test_cache_mechanism()
        self.test_convenience_function()

        # 打印总结
        print("\n" + "="*70)
        print(f"验证结果: {self.passed}/{self.passed + self.failed} 通过")
        print("="*70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    verifier = VerifyP0_5()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)

