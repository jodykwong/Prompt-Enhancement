#!/usr/bin/env python3
"""
Setup script for prompt-enhancement package

Install with:
    pip install .
    pip install -e .  # 开发模式

Upload to PyPI:
    python setup.py sdist bdist_wheel
    twine upload dist/*
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent.parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="prompt-enhancement",
    version="2.0.0",
    author="Jody Kwong",
    author_email="jodykwong@example.com",
    description="AI-powered prompt enhancement tool for development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jodykwong/Prompt-Enhancement",
    project_urls={
        "Bug Tracker": "https://github.com/jodykwong/Prompt-Enhancement/issues",
        "Documentation": "https://github.com/jodykwong/Prompt-Enhancement#readme",
        "Source Code": "https://github.com/jodykwong/Prompt-Enhancement",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "prompt-enhance-install=prompt_enhancement.cli:install_command",
            "prompt-enhance-setup=prompt_enhancement.cli:setup_command",
            "prompt-enhance-verify=prompt_enhancement.cli:verify_command",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
