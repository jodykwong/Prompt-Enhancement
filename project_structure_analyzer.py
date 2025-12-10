#!/usr/bin/env python3
"""
项目结构分析器 - Project Structure Analyzer

这个模块提供自动分析项目目录结构的功能，包括：
1. 生成项目目录树（限制深度为 3 层）
2. 识别关键目录（src/, tests/, docs/, config/ 等）
3. 识别入口文件（main.py, index.js, app.py 等）
4. 识别配置文件（.env, config.yaml, settings.py 等）
5. 统计文件和目录总数

**使用示例**：

```python
from project_structure_analyzer import analyze_project_structure

# 分析项目结构
structure = analyze_project_structure("/path/to/project")

print(f"关键目录: {structure['key_directories']}")
print(f"入口文件: {structure['entry_files']}")
print(f"配置文件: {structure['config_files']}")
print(f"目录树:\\n{structure['directory_tree']}")
```

**返回值结构**：

```python
{
    "directory_tree": "src/\\n  components/\\n  utils/\\n...",
    "key_directories": ["src", "tests", "docs"],
    "entry_files": ["main.py", "app.py"],
    "config_files": [".env", "config.yaml"],
    "total_files": 42,
    "total_directories": 8
}
```

**关键目录识别**：
- 源代码: src/, app/, lib/, source/
- 测试: tests/, test/, __tests__/, spec/
- 文档: docs/, doc/, documentation/
- 配置: config/, settings/, conf/
- 脚本: scripts/, script/

**忽略目录**：
- node_modules/, __pycache__/, .git/, venv/, dist/, build/
- .venv/, env/, .env/, .next/, .nuxt/, .cache/
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ProjectStructureAnalyzer:
    """项目结构分析器类"""

    # 关键目录模式
    KEY_DIRECTORIES = {
        "source": ["src", "app", "lib", "source", "code"],
        "tests": ["tests", "test", "__tests__", "spec", "specs"],
        "docs": ["docs", "doc", "documentation", "docs-src"],
        "config": ["config", "settings", "conf", "configuration"],
        "scripts": ["scripts", "script", "bin", "tools"],
        "build": ["build", "dist", "out", "output"],
    }

    # 入口文件模式
    ENTRY_FILES = [
        "main.py", "app.py", "server.py", "manage.py", "wsgi.py",
        "index.js", "index.ts", "index.tsx", "app.js", "app.ts",
        "server.js", "start.js", "main.go", "main.rs",
        "index.html", "App.tsx", "App.jsx", "App.vue",
    ]

    # 配置文件模式
    CONFIG_FILES = [
        ".env", ".env.local", ".env.example", ".env.production",
        "config.yaml", "config.yml", "config.json", "config.toml",
        "settings.py", "settings.json", "settings.yaml",
        "docker-compose.yml", "docker-compose.yaml",
        ".dockerignore", "Dockerfile",
        "tsconfig.json", "webpack.config.js", "vite.config.js",
        "jest.config.js", "pytest.ini", "setup.cfg",
    ]

    # 忽略的目录
    IGNORE_DIRS = {
        "node_modules", "__pycache__", ".git", "venv", ".venv",
        "dist", "build", "env", ".env", ".next", ".nuxt",
        ".cache", ".pytest_cache", ".mypy_cache", "*.egg-info",
        ".idea", ".vscode", ".DS_Store", "target", "out",
    }

    def __init__(self, project_path: str, max_depth: int = 3):
        """
        初始化项目结构分析器

        Args:
            project_path: 项目路径
            max_depth: 目录树最大深度（默认 3）
        """
        self.project_path = Path(project_path)
        self.max_depth = max_depth
        self.key_dirs_found = set()
        self.entry_files_found = []
        self.config_files_found = []
        self.total_files = 0
        self.total_directories = 0

    def analyze(self) -> Dict[str, Any]:
        """
        分析项目结构

        Returns:
            包含项目结构信息的字典
        """
        if not self.project_path.exists():
            logger.warning(f"项目路径不存在: {self.project_path}")
            return {
                "directory_tree": "",
                "key_directories": [],
                "entry_files": [],
                "config_files": [],
                "total_files": 0,
                "total_directories": 0,
            }

        try:
            # 生成目录树
            directory_tree = self._generate_tree()

            # 扫描项目结构
            self._scan_directory(self.project_path, 0)

            return {
                "directory_tree": directory_tree,
                "key_directories": sorted(list(self.key_dirs_found)),
                "entry_files": sorted(self.entry_files_found),
                "config_files": sorted(self.config_files_found),
                "total_files": self.total_files,
                "total_directories": self.total_directories,
            }
        except Exception as e:
            logger.warning(f"分析项目结构时出错: {e}")
            return {
                "directory_tree": "",
                "key_directories": [],
                "entry_files": [],
                "config_files": [],
                "total_files": 0,
                "total_directories": 0,
            }

    def _generate_tree(self, path: Path = None, prefix: str = "", depth: int = 0) -> str:
        """生成目录树"""
        if path is None:
            path = self.project_path

        if depth >= self.max_depth:
            return ""

        tree = ""
        try:
            items = sorted(path.iterdir())
            dirs = [item for item in items if item.is_dir() and item.name not in self.IGNORE_DIRS]
            files = [item for item in items if item.is_file()]

            # 显示文件（最多 5 个）
            for i, file in enumerate(files[:5]):
                tree += f"{prefix}  {file.name}\n"

            if len(files) > 5:
                tree += f"{prefix}  ... 还有 {len(files) - 5} 个文件\n"

            # 显示目录
            for i, dir_item in enumerate(dirs[:5]):
                is_last = i == len(dirs) - 1
                tree += f"{prefix}{dir_item.name}/\n"
                subtree = self._generate_tree(dir_item, prefix + "  ", depth + 1)
                tree += subtree

            if len(dirs) > 5:
                tree += f"{prefix}... 还有 {len(dirs) - 5} 个目录\n"

        except PermissionError:
            logger.warning(f"无法访问目录: {path}")

        return tree

    def _scan_directory(self, path: Path, depth: int) -> None:
        """扫描目录以识别关键目录和文件"""
        if depth > self.max_depth or path.name in self.IGNORE_DIRS:
            return

        try:
            for item in path.iterdir():
                # 跳过隐藏文件，除了特定的配置文件
                if item.name.startswith(".") and item.name not in [".env", ".env.example", ".env.local", ".env.production"]:
                    continue

                if item.is_dir():
                    if item.name not in self.IGNORE_DIRS:
                        self.total_directories += 1
                        self._check_key_directory(item.name)
                        self._scan_directory(item, depth + 1)
                elif item.is_file():
                    self.total_files += 1
                    self._check_entry_file(item.name)
                    self._check_config_file(item.name)

        except PermissionError:
            logger.warning(f"无法访问目录: {path}")

    def _check_key_directory(self, dir_name: str) -> None:
        """检查是否为关键目录"""
        for category, patterns in self.KEY_DIRECTORIES.items():
            if dir_name in patterns:
                self.key_dirs_found.add(dir_name)

    def _check_entry_file(self, file_name: str) -> None:
        """检查是否为入口文件"""
        if file_name in self.ENTRY_FILES:
            self.entry_files_found.append(file_name)

    def _check_config_file(self, file_name: str) -> None:
        """检查是否为配置文件"""
        if file_name in self.CONFIG_FILES:
            self.config_files_found.append(file_name)


def analyze_project_structure(project_path: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    分析项目结构的便捷函数

    Args:
        project_path: 项目路径
        max_depth: 目录树最大深度（默认 3）

    Returns:
        包含项目结构信息的字典
    """
    analyzer = ProjectStructureAnalyzer(project_path, max_depth)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."

    result = analyze_project_structure(project_path)

    print("\n" + "=" * 70)
    print("项目结构分析结果")
    print("=" * 70)
    print(f"\n项目路径: {project_path}\n")

    print("关键目录:")
    if result["key_directories"]:
        for dir_name in result["key_directories"]:
            print(f"  • {dir_name}")
    else:
        print("  未检测到")

    print("\n入口文件:")
    if result["entry_files"]:
        for file_name in result["entry_files"]:
            print(f"  • {file_name}")
    else:
        print("  未检测到")

    print("\n配置文件:")
    if result["config_files"]:
        for file_name in result["config_files"]:
            print(f"  • {file_name}")
    else:
        print("  未检测到")

    print(f"\n统计信息:")
    print(f"  文件总数: {result['total_files']}")
    print(f"  目录总数: {result['total_directories']}")

    print(f"\n目录树 (深度限制: 3):")
    print(result["directory_tree"] if result["directory_tree"] else "  (空)")

    print("=" * 70)

