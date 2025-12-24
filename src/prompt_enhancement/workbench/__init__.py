"""
Workbench Integration - v1.4

本地prompt测试、评估、比较和版本管理系统。

5个核心子模块:
  1. test_generator.py: 测试用例生成器
     - 边界值测试
     - 等价类测试
     - 领域特定测试

  2. variant_comparator.py: 变体比较器
     - 并排比较多个版本
     - 评分维度：完整性、准确性、格式、响应时间、token效率

  3. quality_grader.py: 质量评分器
     - 5分制评分系统
     - 基于多个评估维度

  4. version_manager.py: 版本管理器
     - 记录版本历史
     - 支持版本恢复
     - 显示版本diff

  5. export_generator.py: 代码导出器
     - 导出Python代码
     - 导出TypeScript代码
     - 导出cURL命令
"""

__all__ = [
    'TestGenerator',
    'VariantComparator',
    'QualityGrader',
    'VersionManager',
    'ExportGenerator'
]
