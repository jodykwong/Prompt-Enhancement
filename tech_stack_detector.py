#!/usr/bin/env python3
"""
技术栈检测器 - Tech Stack Detector

这个模块提供自动检测项目使用的技术栈功能，包括：
1. 前端框架（React, Vue, Angular, Svelte 等）
2. 后端语言和框架（Python, Node.js, Java, Go, Django, Flask 等）
3. 数据库（PostgreSQL, MySQL, MongoDB 等）
4. 构建工具（Webpack, Vite, npm, pip 等）

**使用示例**：

```python
from tech_stack_detector import detect_tech_stack

# 检测项目技术栈
tech_stack = detect_tech_stack("/path/to/project")

print(f"前端框架: {tech_stack['frontend']}")
print(f"后端语言: {tech_stack['backend']}")
print(f"数据库: {tech_stack['database']}")
print(f"构建工具: {tech_stack['build_tools']}")
```

**返回值结构**：

```python
{
    "frontend": ["React", "TypeScript"],
    "backend": ["Python", "Django"],
    "database": ["PostgreSQL"],
    "build_tools": ["npm", "Webpack"],
    "detected_files": {
        "package.json": True,
        "requirements.txt": True,
        "docker-compose.yml": False
    }
}
```

**支持的技术栈**：

- **前端框架**: React, Vue, Angular, Svelte, Next.js, Nuxt, Gatsby
- **后端语言**: Python, Node.js, Java, Go, Ruby, PHP, C#
- **后端框架**: Django, Flask, Express, Spring Boot, Gin, Rails, Laravel
- **数据库**: PostgreSQL, MySQL, MongoDB, Redis, SQLite, MariaDB
- **构建工具**: npm, yarn, pnpm, pip, Maven, Gradle, Cargo, Go modules
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TechStackDetector:
    """技术栈检测器类"""

    # 技术栈映射表
    TECH_STACK_MAP = {
        "frontend": {
            "react": ["react", "react-dom"],
            "vue": ["vue"],
            "angular": ["@angular/core"],
            "svelte": ["svelte"],
            "next.js": ["next"],
            "nuxt": ["nuxt"],
            "gatsby": ["gatsby"],
            "remix": ["@remix-run/react"],
        },
        "backend": {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "node.js": ["package.json"],
            "java": ["pom.xml", "build.gradle"],
            "go": ["go.mod", "go.sum"],
            "ruby": ["Gemfile"],
            "php": ["composer.json"],
            "c#": ["*.csproj", "*.sln"],
        },
        "frameworks": {
            "django": ["django"],
            "flask": ["flask"],
            "express": ["express"],
            "spring boot": ["spring-boot"],
            "gin": ["github.com/gin-gonic/gin"],
            "rails": ["rails"],
            "laravel": ["laravel/framework"],
            "fastapi": ["fastapi"],
        },
        "database": {
            "postgresql": ["psycopg2", "pg8000", "asyncpg"],
            "mysql": ["mysql-connector-python", "pymysql", "mysqlclient"],
            "mongodb": ["pymongo", "motor", "mongodb"],
            "redis": ["redis", "aioredis"],
            "sqlite": ["sqlite3"],
            "mariadb": ["mariadb"],
        },
        "build_tools": {
            "npm": ["package.json"],
            "yarn": ["yarn.lock"],
            "pnpm": ["pnpm-lock.yaml"],
            "pip": ["requirements.txt", "setup.py"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle"],
            "cargo": ["Cargo.toml"],
            "go modules": ["go.mod"],
        },
    }

    def __init__(self, project_path: str):
        """
        初始化技术栈检测器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            logger.warning(f"项目路径不存在: {project_path}")

    def detect(self) -> Dict[str, Any]:
        """
        检测项目技术栈

        Returns:
            包含检测结果的字典，结构如下：
            {
                "frontend": ["React", "TypeScript"],
                "backend": ["Python", "Django"],
                "database": ["PostgreSQL"],
                "build_tools": ["npm"],
                "detected_files": {...}
            }
        """
        result = {
            "frontend": [],
            "backend": [],
            "database": [],
            "build_tools": [],
            "detected_files": {},
        }

        if not self.project_path.exists():
            return result

        # 检测各个技术栈
        result["frontend"] = self._detect_frontend()
        result["backend"] = self._detect_backend()
        result["database"] = self._detect_database()
        result["build_tools"] = self._detect_build_tools()
        result["detected_files"] = self._get_detected_files()

        return result

    def _detect_frontend(self) -> List[str]:
        """检测前端框架"""
        detected = set()
        package_json_path = self.project_path / "package.json"

        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_data = json.load(f)
                    deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {}),
                    }

                    for framework, packages in self.TECH_STACK_MAP["frontend"].items():
                        if any(pkg in deps for pkg in packages):
                            detected.add(framework.title())
            except Exception as e:
                logger.warning(f"读取 package.json 失败: {e}")

        return sorted(list(detected))

    def _detect_backend(self) -> List[str]:
        """检测后端语言和框架"""
        detected = set()

        # 检测后端语言
        for lang, files in self.TECH_STACK_MAP["backend"].items():
            if any((self.project_path / file).exists() for file in files):
                # 特殊处理 Node.js 的大小写
                if lang == "node.js":
                    detected.add("Node.js")
                else:
                    detected.add(lang.title())

        # 检测框架
        detected.update(self._detect_frameworks())

        return sorted(list(detected))

    def _detect_frameworks(self) -> Set[str]:
        """检测后端框架"""
        detected = set()

        # 检查 requirements.txt（Python 框架）
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for framework, packages in self.TECH_STACK_MAP["frameworks"].items():
                        if any(pkg.lower() in content for pkg in packages):
                            detected.add(framework.title())
            except Exception as e:
                logger.warning(f"读取 requirements.txt 失败: {e}")

        # 检查 package.json（Node.js 框架）
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_data = json.load(f)
                    deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {}),
                    }

                    for framework, packages in self.TECH_STACK_MAP["frameworks"].items():
                        if any(pkg in deps for pkg in packages):
                            detected.add(framework.title())
            except Exception as e:
                logger.warning(f"读取 package.json 失败: {e}")

        return detected

    def _detect_database(self) -> List[str]:
        """检测数据库"""
        detected = set()

        # 检查 requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for db, packages in self.TECH_STACK_MAP["database"].items():
                        if any(pkg.lower() in content for pkg in packages):
                            detected.add(db.title())
            except Exception as e:
                logger.warning(f"读取 requirements.txt 失败: {e}")

        # 检查 package.json
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_data = json.load(f)
                    deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {}),
                    }

                    for db, packages in self.TECH_STACK_MAP["database"].items():
                        if any(pkg in deps for pkg in packages):
                            detected.add(db.title())
            except Exception as e:
                logger.warning(f"读取 package.json 失败: {e}")

        return sorted(list(detected))

    def _detect_build_tools(self) -> List[str]:
        """检测构建工具"""
        detected = set()

        for tool, files in self.TECH_STACK_MAP["build_tools"].items():
            if any((self.project_path / file).exists() for file in files):
                detected.add(tool.title())

        return sorted(list(detected))

    def _get_detected_files(self) -> Dict[str, bool]:
        """获取检测到的文件列表"""
        files_to_check = [
            "package.json",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "pom.xml",
            "build.gradle",
            "go.mod",
            "Cargo.toml",
            "Gemfile",
            "composer.json",
            "docker-compose.yml",
            "Dockerfile",
            ".env",
            ".env.example",
        ]

        return {
            file: (self.project_path / file).exists() for file in files_to_check
        }


def detect_tech_stack(project_path: str) -> Dict[str, Any]:
    """
    检测项目技术栈的便捷函数

    Args:
        project_path: 项目根目录路径

    Returns:
        包含检测结果的字典

    Example:
        >>> tech_stack = detect_tech_stack("/path/to/project")
        >>> print(tech_stack["frontend"])
        ['React', 'Typescript']
    """
    detector = TechStackDetector(project_path)
    return detector.detect()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python tech_stack_detector.py <project_path>")
        print("示例: python tech_stack_detector.py /path/to/project")
        sys.exit(1)

    project_path = sys.argv[1]
    result = detect_tech_stack(project_path)

    print("\n" + "=" * 60)
    print("技术栈检测结果")
    print("=" * 60)
    print(f"项目路径: {project_path}\n")

    print(f"前端框架: {', '.join(result['frontend']) or '未检测到'}")
    print(f"后端语言: {', '.join(result['backend']) or '未检测到'}")
    print(f"数据库: {', '.join(result['database']) or '未检测到'}")
    print(f"构建工具: {', '.join(result['build_tools']) or '未检测到'}")

    print("\n检测到的文件:")
    for file, exists in result["detected_files"].items():
        symbol = "✓" if exists else "✗"
        print(f"  {symbol} {file}")

    print("=" * 60)

