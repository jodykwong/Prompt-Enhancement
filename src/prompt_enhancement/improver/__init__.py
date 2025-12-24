"""
Prompt Improver - v1.4

自动优化现有prompt的工具。

提供5个优化策略:
  1. Chain-of-Thought注入 (CoT)
  2. 示例标准化
  3. 示例丰富化
  4. 指令清晰化
  5. 变量标记

模块结构:
  - improver.py: 核心PromptImprover编排类
  - strategies/: 各个优化策略实现
  - feedback_loop.py: 反馈循环处理
"""

__all__ = ['PromptImprover', 'FeedbackLoop']
