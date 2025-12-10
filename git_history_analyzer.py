#!/usr/bin/env python3
"""
Git 历史分析器 - Git History Analyzer

这个模块提供自动分析项目 Git 提交历史的功能，包括：
1. 最近的提交记录（hash、author、date、message）
2. 最近修改的文件列表
3. 活跃分支列表
4. 当前分支名称
5. 未提交的更改状态

**使用示例**：

```python
from git_history_analyzer import analyze_git_history

# 分析 Git 历史
history = analyze_git_history("/path/to/project", max_commits=5)

print(f"最近提交: {history['recent_commits']}")
print(f"修改文件: {history['modified_files']}")
print(f"当前分支: {history['current_branch']}")
print(f"未提交更改: {history['has_uncommitted_changes']}")
```

**返回值结构**：

```python
{
    "recent_commits": [
        {
            "hash": "abc1234",
            "author": "John Doe",
            "date": "2025-12-09",
            "message": "Fix bug in parser"
        }
    ],
    "modified_files": ["src/main.py", "tests/test_main.py"],
    "active_branches": ["main", "develop", "feature/new-feature"],
    "current_branch": "main",
    "has_uncommitted_changes": False,
    "is_git_repo": True
}
```
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class GitHistoryAnalyzer:
    """Git 历史分析器类"""

    def __init__(self, project_path: str, max_commits: int = 5):
        """
        初始化 Git 历史分析器

        Args:
            project_path: 项目路径
            max_commits: 最多获取的提交数（默认 5）
        """
        self.project_path = Path(project_path)
        self.max_commits = max_commits
        self.is_git_repo = False

    def analyze(self) -> Dict[str, Any]:
        """
        分析 Git 历史

        Returns:
            包含 Git 历史信息的字典
        """
        if not self.project_path.exists():
            logger.warning(f"项目路径不存在: {self.project_path}")
            return self._empty_result()

        # 检查是否是 Git 仓库
        if not self._is_git_repository():
            logger.warning(f"项目不是 Git 仓库: {self.project_path}")
            return self._empty_result()

        self.is_git_repo = True

        result = {
            "recent_commits": self._get_recent_commits(),
            "modified_files": self._get_modified_files(),
            "active_branches": self._get_active_branches(),
            "current_branch": self._get_current_branch(),
            "has_uncommitted_changes": self._has_uncommitted_changes(),
            "is_git_repo": True,
        }

        return result

    def _is_git_repository(self) -> bool:
        """检查是否是 Git 仓库"""
        git_dir = self.project_path / ".git"
        return git_dir.exists()

    def _run_git_command(self, command: List[str]) -> str:
        """
        运行 Git 命令

        Args:
            command: Git 命令列表

        Returns:
            命令输出
        """
        try:
            result = subprocess.run(
                command,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning(f"Git 命令超时: {' '.join(command)}")
            return ""
        except Exception as e:
            logger.warning(f"Git 命令执行失败: {e}")
            return ""

    def _get_recent_commits(self) -> List[Dict[str, str]]:
        """获取最近的提交记录"""
        commits = []
        try:
            # 使用 git log 获取最近的提交
            output = self._run_git_command(
                [
                    "git",
                    "log",
                    f"-{self.max_commits}",
                    "--format=%H|%an|%ai|%s",
                ]
            )

            if not output:
                return commits

            for line in output.split("\n"):
                if not line.strip():
                    continue

                parts = line.split("|", 3)
                if len(parts) >= 4:
                    commit_hash = parts[0][:7]  # 缩短 hash
                    author = parts[1]
                    date = parts[2].split()[0]  # 只取日期部分
                    message = parts[3]

                    commits.append(
                        {
                            "hash": commit_hash,
                            "author": author,
                            "date": date,
                            "message": message,
                        }
                    )

        except Exception as e:
            logger.warning(f"获取提交记录失败: {e}")

        return commits

    def _get_modified_files(self) -> List[str]:
        """获取最近修改的文件列表"""
        files = set()
        try:
            # 获取工作区修改的文件
            output = self._run_git_command(["git", "status", "--porcelain"])
            for line in output.split("\n"):
                if line.strip():
                    # 格式: " M file.py" 或 "?? file.py"
                    file_path = line[3:].strip()
                    if file_path:
                        files.add(file_path)

            # 获取最近一次提交修改的文件
            output = self._run_git_command(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
            )
            for line in output.split("\n"):
                if line.strip():
                    files.add(line.strip())

        except Exception as e:
            logger.warning(f"获取修改文件列表失败: {e}")

        return sorted(list(files))

    def _get_active_branches(self) -> List[str]:
        """获取活跃分支列表"""
        branches = []
        try:
            output = self._run_git_command(["git", "branch", "-a"])
            for line in output.split("\n"):
                if line.strip():
                    # 移除 * 和空格
                    branch = line.strip().lstrip("*").strip()
                    # 移除 remotes/ 前缀
                    if branch.startswith("remotes/"):
                        branch = branch.replace("remotes/", "")
                    if branch and branch not in branches:
                        branches.append(branch)

        except Exception as e:
            logger.warning(f"获取分支列表失败: {e}")

        return branches

    def _get_current_branch(self) -> str:
        """获取当前分支名称"""
        try:
            output = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            return output if output else "unknown"
        except Exception as e:
            logger.warning(f"获取当前分支失败: {e}")
            return "unknown"

    def _has_uncommitted_changes(self) -> bool:
        """检查是否有未提交的更改"""
        try:
            output = self._run_git_command(["git", "status", "--porcelain"])
            return bool(output.strip())
        except Exception as e:
            logger.warning(f"检查未提交更改失败: {e}")
            return False

    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "recent_commits": [],
            "modified_files": [],
            "active_branches": [],
            "current_branch": "",
            "has_uncommitted_changes": False,
            "is_git_repo": False,
        }


def analyze_git_history(project_path: str, max_commits: int = 5) -> Dict[str, Any]:
    """
    分析项目 Git 历史

    Args:
        project_path: 项目路径
        max_commits: 最多获取的提交数（默认 5）

    Returns:
        包含 Git 历史信息的字典

    Example:
        >>> history = analyze_git_history("/path/to/project")
        >>> print(history['current_branch'])
        'main'
    """
    analyzer = GitHistoryAnalyzer(project_path, max_commits)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."

    result = analyze_git_history(project_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))

