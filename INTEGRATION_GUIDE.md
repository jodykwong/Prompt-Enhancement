# 🔗 集成指南

**版本**: P0.6 | **最后更新**: 2025-12-10

本指南说明如何将 Prompt Enhancement 系统集成到不同的平台和工具中。

---

## 📚 目录

1. [集成概览](#集成概览)
2. [Python 项目集成](#python-项目集成)
3. [CLI 工具集成](#cli-工具集成)
4. [Web 服务集成](#web-服务集成)
5. [IDE 插件集成](#ide-插件集成)
6. [API 服务集成](#api-服务集成)
7. [最佳实践](#最佳实践)

---

## 集成概览

### 支持的集成方式

```
Prompt Enhancement
├── Python 包 (直接导入)
├── CLI 命令行工具
├── REST API 服务
├── IDE 插件 (VS Code, PyCharm)
└── 框架集成 (Django, FastAPI, Flask)
```

### 集成难度和工作量

| 集成方式 | 难度 | 工作量 | 推荐场景 |
|--------|-----|--------|---------|
| Python 包 | ⭐ 低 | 15 分钟 | 脚本、自动化 |
| CLI 命令 | ⭐⭐ 中 | 30 分钟 | 命令行用户 |
| Flask/FastAPI | ⭐⭐ 中 | 1 小时 | Web 服务 |
| IDE 插件 | ⭐⭐⭐ 高 | 4-8 小时 | IDE 集成 |

---

## Python 项目集成

### 方式 1: 直接导入 (最简单)

**适用于**: 任何 Python 项目

**集成步骤**:

1. 复制源文件到你的项目
```bash
cp -r Prompt-Enhancement/src/* your-project/lib/
```

2. 在代码中导入使用
```python
from lib.enhanced_prompt_generator import enhance_prompt_with_context

async def generate_docs(feature_name: str):
    result = await enhance_prompt_with_context(
        f"为 {feature_name} 生成文档",
        project_path="./"
    )
    return result["enhanced"]
```

### 方式 2: 作为包安装 (推荐)

**适用于**: 包管理和版本控制重要的项目

1. 准备包
```bash
# 创建 setup.py
cat > setup.py << 'EOF'
from setuptools import setup

setup(
    name="prompt-enhancement",
    version="0.6.0",
    description="Intelligent prompt enhancement system",
    packages=["prompt_enhancement"],
    install_requires=[
        "openai>=1.3.0",
        "python-dotenv>=0.19.0",
    ],
)
EOF
```

2. 安装包
```bash
pip install -e .  # 开发模式
# 或
pip install .      # 安装
```

3. 在项目中使用
```python
from prompt_enhancement import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context("你的提示词")
    print(result["enhanced"])
```

### 方式 3: 子模块集成

**适用于**: 多个项目共享

1. 添加为 Git 子模块
```bash
git submodule add https://github.com/your/prompt-enhancement.git lib/prompt-enhancement
```

2. 更新子模块
```bash
git submodule update --init --recursive
```

3. 在代码中使用
```python
import sys
sys.path.insert(0, "lib/prompt-enhancement")
from enhanced_prompt_generator import enhance_prompt_with_context
```

### 示例: Django 项目集成

```python
# myapp/utils.py
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

def generate_enhanced_prompt(prompt: str) -> str:
    """在 Django 视图中使用的包装函数"""
    try:
        result = asyncio.run(
            enhance_prompt_with_context(
                prompt,
                project_path="./"
            )
        )
        return result["enhanced"]
    except Exception as e:
        logger.error(f"提示词增强失败: {e}")
        return prompt  # 失败时返回原始提示词

# views.py
from django.http import JsonResponse
from .utils import generate_enhanced_prompt

def enhance_api(request):
    prompt = request.GET.get("prompt")
    enhanced = generate_enhanced_prompt(prompt)
    return JsonResponse({"enhanced": enhanced})
```

---

## CLI 工具集成

### 创建命令行工具

```python
#!/usr/bin/env python3
"""
Prompt Enhancement CLI 工具
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from enhanced_prompt_generator import enhance_prompt_with_context

def main():
    parser = argparse.ArgumentParser(
        description="智能提示词增强工具"
    )

    parser.add_argument(
        "prompt",
        help="要增强的提示词"
    )

    parser.add_argument(
        "-p", "--project",
        help="项目路径 (默认: 当前目录)",
        default="./"
    )

    parser.add_argument(
        "-o", "--output",
        help="输出文件 (默认: 打印到控制台)",
        default=None
    )

    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=60,
        help="超时时间 (秒，默认: 60)"
    )

    args = parser.parse_args()

    # 运行增强
    async def enhance():
        result = await enhance_prompt_with_context(
            args.prompt,
            project_path=args.project,
            timeout=args.timeout
        )
        return result

    result = asyncio.run(enhance())

    # 输出结果
    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = result["enhanced"]

    if args.output:
        # 写入文件
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✓ 结果已保存到: {args.output}")
    else:
        # 打印到控制台
        print(output)

if __name__ == "__main__":
    main()
```

**使用示例**:

```bash
# 基本使用
./enhance_cli.py "优化代码性能"

# 指定项目路径
./enhance_cli.py "修复 bug" --project /path/to/project

# 保存到文件
./enhance_cli.py "写文档" --output result.md

# JSON 格式输出
./enhance_cli.py "测试" --json | jq .enhanced
```

---

## Web 服务集成

### FastAPI 集成

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio
import os

app = FastAPI(title="Prompt Enhancement API")

class PromptRequest(BaseModel):
    prompt: str
    project_path: str = None
    timeout: int = 60

class PromptResponse(BaseModel):
    original: str
    enhanced: str
    success: bool
    processing_time: float
    context_injected: bool = None

@app.post("/enhance", response_model=PromptResponse)
async def enhance_prompt(request: PromptRequest):
    """增强提示词"""
    try:
        result = await enhance_prompt_with_context(
            request.prompt,
            project_path=request.project_path,
            timeout=request.timeout
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "增强失败")
            )

        return PromptResponse(**{
            "original": result["original"],
            "enhanced": result["enhanced"],
            "success": result["success"],
            "processing_time": result["processing_time"],
            "context_injected": result.get("context_injected")
        })

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="请求超时，请增加超时时间"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("DEEPSEEK_API_KEY"))
    }

@app.get("/")
async def root():
    """API 信息"""
    return {
        "name": "Prompt Enhancement API",
        "version": "0.6.0",
        "endpoints": {
            "enhance": "POST /enhance",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**部署和使用**:

```bash
# 安装 FastAPI
pip install fastapi uvicorn

# 运行服务器
python main.py

# 发送请求
curl -X POST "http://localhost:8000/enhance" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "优化数据库查询",
    "project_path": "/path/to/project",
    "timeout": 60
  }'
```

### Flask 集成

```python
# app.py
from flask import Flask, request, jsonify
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio

app = Flask(__name__)

@app.route("/enhance", methods=["POST"])
def enhance():
    """增强提示词端点"""
    data = request.get_json()
    prompt = data.get("prompt")
    project_path = data.get("project_path")
    timeout = data.get("timeout", 60)

    if not prompt:
        return jsonify({"error": "prompt 参数缺失"}), 400

    try:
        # 在 Flask 中运行异步函数
        result = asyncio.run(
            enhance_prompt_with_context(
                prompt,
                project_path=project_path,
                timeout=timeout
            )
        )

        return jsonify({
            "enhanced": result["enhanced"],
            "success": result["success"],
            "processing_time": result["processing_time"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

## IDE 插件集成

### VS Code 扩展 (示例)

```json
{
  "name": "prompt-enhancement",
  "displayName": "Prompt Enhancement",
  "version": "0.1.0",
  "description": "在 VS Code 中增强提示词",
  "engines": {
    "vscode": "^1.60.0"
  },
  "activationEvents": [
    "onCommand:prompt-enhancement.enhance"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "prompt-enhancement.enhance",
        "title": "增强选中的提示词"
      }
    ],
    "keybindings": [
      {
        "command": "prompt-enhancement.enhance",
        "key": "ctrl+shift+e",
        "mac": "cmd+shift+e"
      }
    ]
  }
}
```

---

## API 服务集成

### REST API 客户端

```python
# client.py
import requests
import asyncio
from typing import Optional

class PromptEnhancementClient:
    """提示词增强 API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def enhance(
        self,
        prompt: str,
        project_path: Optional[str] = None,
        timeout: int = 60
    ) -> dict:
        """增强提示词"""
        response = requests.post(
            f"{self.base_url}/enhance",
            json={
                "prompt": prompt,
                "project_path": project_path,
                "timeout": timeout
            }
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 错误: {response.text}")

    def health_check(self) -> dict:
        """检查 API 健康状态"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# 使用示例
client = PromptEnhancementClient()

# 同步调用
result = asyncio.run(
    client.enhance("优化性能", project_path="./")
)
print(result["enhanced"])

# 健康检查
health = client.health_check()
print(f"API 状态: {health['status']}")
```

---

## 最佳实践

### 1. 错误处理

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def safe_enhance(prompt: str, project_path: str = None) -> str:
    """安全的增强函数，包含完整错误处理"""
    try:
        result = await enhance_prompt_with_context(
            prompt,
            project_path=project_path,
            timeout=60
        )

        if result["success"]:
            return result["enhanced"]
        else:
            # 增强失败，返回原始提示词
            logger.warning(f"增强失败: {result.get('error')}")
            return prompt

    except asyncio.TimeoutError:
        logger.error("增强请求超时")
        return prompt

    except Exception as e:
        logger.error(f"增强异常: {e}")
        return prompt
```

### 2. 性能考虑

```python
# ✅ 好: 复用生成器实例
generator = EnhancedPromptGenerator()
for prompt in prompts:
    result = await generator.enhance(prompt, project_path)

# ❌ 不好: 每次创建新实例
for prompt in prompts:
    result = await enhance_prompt_with_context(prompt, project_path)
```

### 3. 环境配置

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxx
PROMPT_ENHANCEMENT_TIMEOUT=60
PROMPT_ENHANCEMENT_CACHE_SIZE=100

# 在代码中读取
import os
from dotenv import load_dotenv

load_dotenv()

timeout = int(os.getenv("PROMPT_ENHANCEMENT_TIMEOUT", "60"))
cache_size = int(os.getenv("PROMPT_ENHANCEMENT_CACHE_SIZE", "100"))
```

### 4. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

async def enhance_with_logging(prompt: str, project_path: str):
    logger.info(f"开始增强提示词: {prompt[:50]}...")

    try:
        result = await enhance_prompt_with_context(
            prompt,
            project_path=project_path
        )

        logger.info(
            f"增强成功，耗时 {result['processing_time']:.2f}s"
        )
        return result

    except Exception as e:
        logger.error(f"增强失败: {e}", exc_info=True)
        raise
```

---

## 常见集成问题

### Q1: 在 Web 框架中运行异步代码？

**A**: 使用 `asyncio.run()` 或框架的异步支持

```python
# Django (同步上下文)
def my_view(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        enhance_prompt_with_context("prompt")
    )
    loop.close()
    return JsonResponse(result)

# FastAPI (异步上下文)
@app.post("/enhance")
async def enhance_api(request):
    result = await enhance_prompt_with_context("prompt")
    return result
```

### Q2: 如何处理多个用户的并发请求？

**A**: 使用连接池和速率限制

```python
from aiolimiter import AsyncLimiter

# 创建限制器: 最多 10 并发，每秒 5 个请求
limiter = AsyncLimiter(10, 1)

async def enhance_with_limit(prompt):
    async with limiter:
        return await enhance_prompt_with_context(prompt)
```

### Q3: 如何在容器中部署？

**A**: 创建 Dockerfile

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## 相关文档

- **[USER_GUIDE.md](USER_GUIDE.md)** - 详细使用指南
- **[API_REFERENCE.md](API_REFERENCE.md)** - API 完整参考
- **[QUICK_START.md](QUICK_START.md)** - 快速开始

---

**集成指南完成！**

有任何集成问题？查看具体框架的文档或联系支持。

---

**作者**: Jodykwong
**最后更新**: 2025-12-10
**版本**: P0.6
