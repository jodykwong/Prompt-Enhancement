#!/usr/bin/env python3
"""
上下文收集器 - Context Collector

这个模块提供整合技术栈、项目结构和 Git 历史的统一上下文收集功能，包括：
1. 整合 P0.1（技术栈检测）、P0.2（项目结构分析）、P0.3（Git 历史）的输出
2. 生成项目摘要
3. 格式化上下文字符串用于提示词增强
4. 实现简单的缓存机制

**使用示例**：

```python
from context_collector import collect_project_context

# 收集项目上下文
context = collect_project_context("/path/to/project")

print(f"技术栈: {context['tech_stack']}")
print(f"项目结构: {context['project_structure']}")
print(f"Git 历史: {context['git_history']}")
print(f"摘要: {context['summary']}")
print(f"格式化上下文:\\n{context['context_string']}")
```

**返回值结构**：

```python
{
    "tech_stack": {...},  # 来自 tech_stack_detector
    "project_structure": {...},  # 来自 project_structure_analyzer
    "git_history": {...},  # 来自 git_history_analyzer
    "summary": "Python Django 项目，包含 React 前端...",
    "context_string": "# 项目上下文\\n\\n## 技术栈\\n..."
}
```
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure
from git_history_analyzer import analyze_git_history

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class ContextCollector:
    """上下文收集器类"""

    def __init__(self, project_path: str):
        """
        初始化上下文收集器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self._cache = {}

    def collect(self) -> Dict[str, Any]:
        """
        收集项目上下文

        Returns:
            包含完整项目上下文的字典
        """
        if not self.project_path.exists():
            logger.warning(f"项目路径不存在: {self.project_path}")
            return self._empty_result()

        # 检查缓存
        cache_key = str(self.project_path.resolve())
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = {
            "tech_stack": self._collect_tech_stack(),
            "project_structure": self._collect_project_structure(),
            "git_history": self._collect_git_history(),
        }

        # 生成摘要和格式化字符串
        result["summary"] = self._generate_summary(result)
        result["context_string"] = self._format_context_string(result)

        # 缓存结果
        self._cache[cache_key] = result

        return result

    def _collect_tech_stack(self) -> Dict[str, Any]:
        """收集技术栈信息"""
        try:
            return detect_tech_stack(str(self.project_path))
        except Exception as e:
            logger.warning(f"收集技术栈失败: {e}")
            return {
                "frontend": [],
                "backend": [],
                "database": [],
                "build_tools": [],
                "detected_files": {},
            }

    def _collect_project_structure(self) -> Dict[str, Any]:
        """收集项目结构信息"""
        try:
            return analyze_project_structure(str(self.project_path))
        except Exception as e:
            logger.warning(f"收集项目结构失败: {e}")
            return {
                "directory_tree": "",
                "key_directories": [],
                "entry_files": [],
                "config_files": [],
                "total_files": 0,
                "total_directories": 0,
            }

    def _collect_git_history(self) -> Dict[str, Any]:
        """收集 Git 历史信息"""
        try:
            return analyze_git_history(str(self.project_path))
        except Exception as e:
            logger.warning(f"收集 Git 历史失败: {e}")
            return {
                "recent_commits": [],
                "modified_files": [],
                "active_branches": [],
                "current_branch": "",
                "has_uncommitted_changes": False,
                "is_git_repo": False,
            }

    def _generate_summary(self, context: Dict[str, Any]) -> str:
        """生成项目摘要"""
        parts = []

        # 技术栈摘要
        tech_stack = context["tech_stack"]
        if tech_stack["backend"]:
            parts.append(f"后端: {', '.join(tech_stack['backend'])}")
        if tech_stack["frontend"]:
            parts.append(f"前端: {', '.join(tech_stack['frontend'])}")
        if tech_stack["database"]:
            parts.append(f"数据库: {', '.join(tech_stack['database'])}")

        # 项目结构摘要
        structure = context["project_structure"]
        if structure["key_directories"]:
            parts.append(f"关键目录: {', '.join(structure['key_directories'][:3])}")

        # Git 摘要
        git = context["git_history"]
        if git["is_git_repo"]:
            parts.append(f"分支: {git['current_branch']}")
            if git["recent_commits"]:
                parts.append(f"最近提交: {git['recent_commits'][0]['message']}")

        return " | ".join(parts) if parts else "项目信息不完整"

    def _format_context_string(self, context: Dict[str, Any]) -> str:
        """格式化上下文字符串"""
        lines = ["# 项目上下文\n"]

        # 技术栈部分
        tech_stack = context["tech_stack"]
        lines.append("## 技术栈")
        if tech_stack["frontend"]:
            lines.append(f"- 前端: {', '.join(tech_stack['frontend'])}")
        if tech_stack["backend"]:
            lines.append(f"- 后端: {', '.join(tech_stack['backend'])}")
        if tech_stack["database"]:
            lines.append(f"- 数据库: {', '.join(tech_stack['database'])}")
        if tech_stack["build_tools"]:
            lines.append(f"- 构建工具: {', '.join(tech_stack['build_tools'])}")
        lines.append("")

        # 项目结构部分
        structure = context["project_structure"]
        lines.append("## 项目结构")
        if structure["key_directories"]:
            lines.append(f"- 关键目录: {', '.join(structure['key_directories'])}")
        if structure["entry_files"]:
            lines.append(f"- 入口文件: {', '.join(structure['entry_files'][:5])}")
        if structure["config_files"]:
            lines.append(f"- 配置文件: {', '.join(structure['config_files'][:5])}")
        lines.append(f"- 文件总数: {structure['total_files']}")
        lines.append(f"- 目录总数: {structure['total_directories']}")
        lines.append("")

        # BMAD 工作流部分
        structure = context["project_structure"]
        if "bmad_modules" in structure and structure["bmad_modules"]:
            lines.append("## BMAD 平台")
            lines.append(f"此项目基于 BMAD（Business Model Architecture Development）平台")
            lines.append("- 已安装模块:")
            for module_name, module_info in sorted(structure["bmad_modules"].items()):
                if module_info["has_workflows"]:
                    workflows_str = ", ".join(module_info["workflows"][:3])
                    if len(module_info["workflows"]) > 3:
                        workflows_str += f" 等 {len(module_info['workflows'])} 个工作流"
                    lines.append(f"  - **{module_name}**: {workflows_str}")
                else:
                    lines.append(f"  - **{module_name}**: 无活跃工作流")
            lines.append("")

        # Git 历史部分
        git = context["git_history"]
        if git["is_git_repo"]:
            lines.append("## Git 历史")
            lines.append(f"- 当前分支: {git['current_branch']}")
            if git["active_branches"]:
                lines.append(f"- 活跃分支: {', '.join(git['active_branches'][:5])}")
            if git["recent_commits"]:
                lines.append("- 最近提交:")
                for commit in git["recent_commits"][:3]:
                    lines.append(f"  - {commit['hash']}: {commit['message']} ({commit['date']})")
            lines.append(f"- 未提交更改: {'有' if git['has_uncommitted_changes'] else '无'}")
            lines.append("")

        return "\n".join(lines)

    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "tech_stack": {
                "frontend": [],
                "backend": [],
                "database": [],
                "build_tools": [],
                "detected_files": {},
            },
            "project_structure": {
                "directory_tree": "",
                "key_directories": [],
                "entry_files": [],
                "config_files": [],
                "total_files": 0,
                "total_directories": 0,
            },
            "git_history": {
                "recent_commits": [],
                "modified_files": [],
                "active_branches": [],
                "current_branch": "",
                "has_uncommitted_changes": False,
                "is_git_repo": False,
            },
            "summary": "",
            "context_string": "",
        }

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()


def collect_project_context(project_path: str) -> Dict[str, Any]:
    """
    收集项目上下文

    Args:
        project_path: 项目路径

    Returns:
        包含完整项目上下文的字典

    Example:
        >>> context = collect_project_context("/path/to/project")
        >>> print(context['summary'])
        'Python Django 项目，包含 React 前端...'
    """
    collector = ContextCollector(project_path)
    return collector.collect()


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."

    context = collect_project_context(project_path)
    print(context["context_string"])

