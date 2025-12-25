"""
Prompt Enhancement v1.2.3
A project-aware prompt enhancement tool for Claude Code.

v1.2.3 修复:
  - /pe 命令自动执行: 使用 `!` 前缀实现自动执行
  - 根本原因诊断: Slash Command 机制只提供上下文，不自动执行
  - pe.md 精简重写: 从 179 行精简到 13 行

v1.2.1 增强方向:
  - 智能文件发现: 从模糊指令找到最相关的代码文件
  - 符号索引: 快速提取函数/类签名
  - AGENTS.md 自动生成: 为项目生成代理配置
  - 性能优化: 响应时间从30s优化到10s
"""

__version__ = "1.2.3-dev"
__author__ = "Jodykwong"

# Package initialization
