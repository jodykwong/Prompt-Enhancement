"""
Prompt Enhancement - AI-powered prompt optimization for development

A tool that enhances your prompts with AI and project context to make them
clearer, more specific, and easier to execute.

Usage:
    from prompt_enhancement import enhance_prompt_with_context

    result = await enhance_prompt_with_context(
        "修复登录 bug",
        project_path="/path/to/project"
    )
    print(result["enhanced"])

Installation:
    pip install prompt-enhancement
    prompt-enhance-install /path/to/your/project

More info: https://github.com/jodykwong/Prompt-Enhancement
"""

__version__ = "1.0.0"
__author__ = "Jody Kwong"
__license__ = "MIT"

# 导出主要函数和类
try:
    # 注意：这些模块需要从项目根目录导入或复制
    # 目前先提供占位符，实际导入在部署时进行
    pass
except ImportError:
    pass

__all__ = [
    "enhance_prompt_with_context",
    "EnhancedPromptGenerator",
    "AsyncPromptEnhancer",
    "collect_project_context",
]
