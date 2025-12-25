#!/usr/bin/env python3
"""
初始化 kiro-cli 的 bmad 方法支持
Initialize bmad method support for kiro-cli
"""

import os
import json
import sys
from pathlib import Path

def init_bmad_kiro():
    """初始化 kiro-cli 的 bmad 配置"""
    
    project_root = Path(__file__).parent
    kiro_dir = project_root / ".kiro"
    bmad_dir = project_root / "_bmad"
    
    print("🔧 初始化 kiro-cli bmad 方法支持...")
    print(f"📁 项目根目录: {project_root}")
    
    # 1. 检查必要的目录
    if not kiro_dir.exists():
        kiro_dir.mkdir(parents=True)
        print(f"✓ 创建 .kiro 目录")
    
    if not bmad_dir.exists():
        print(f"✗ 错误: _bmad 目录不存在")
        return False
    
    # 2. 创建 kiro 配置文件
    kiro_config = {
        "version": "1.0",
        "bmad_enabled": True,
        "bmad_path": str(bmad_dir),
        "agents_path": str(kiro_dir / "agents"),
        "workflows": {
            "core": str(bmad_dir / "core" / "workflows"),
            "bmm": str(bmad_dir / "bmm" / "workflows"),
            "bmgd": str(bmad_dir / "bmgd" / "workflows"),
            "cis": str(bmad_dir / "cis" / "workflows"),
            "bmb": str(bmad_dir / "bmb" / "workflows")
        }
    }
    
    config_file = kiro_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(kiro_config, f, indent=2)
    print(f"✓ 创建 kiro 配置文件: {config_file}")
    
    # 3. 创建 bmad 初始化脚本
    init_script = project_root / "init_bmad.sh"
    init_script_content = f"""#!/bin/bash
# kiro-cli bmad 初始化脚本

export BMAD_ROOT="{bmad_dir}"
export KIRO_AGENTS_PATH="{kiro_dir}/agents"
export BMAD_WORKFLOWS_PATH="{bmad_dir}/core/workflows"

echo "✓ BMAD 环境变量已设置"
echo "  BMAD_ROOT=$BMAD_ROOT"
echo "  KIRO_AGENTS_PATH=$KIRO_AGENTS_PATH"
echo "  BMAD_WORKFLOWS_PATH=$BMAD_WORKFLOWS_PATH"

# 加载 bmad 工作流
if [ -f "{bmad_dir}/core/tasks/workflow.xml" ]; then
    echo "✓ 检测到 bmad 工作流配置"
fi
"""
    
    with open(init_script, 'w') as f:
        f.write(init_script_content)
    os.chmod(init_script, 0o755)
    print(f"✓ 创建 bmad 初始化脚本: {init_script}")
    
    # 4. 创建 Python 初始化模块
    init_module = project_root / "bmad_kiro_init.py"
    init_module_content = f"""#!/usr/bin/env python3
\"\"\"
kiro-cli bmad 初始化模块
\"\"\"

import os
from pathlib import Path

def setup_bmad_environment():
    \"\"\"设置 bmad 环境变量\"\"\"
    project_root = Path(__file__).parent
    
    os.environ['BMAD_ROOT'] = str(project_root / '_bmad')
    os.environ['KIRO_AGENTS_PATH'] = str(project_root / '.kiro' / 'agents')
    os.environ['BMAD_WORKFLOWS_PATH'] = str(project_root / '_bmad' / 'core' / 'workflows')
    
    return {{
        'BMAD_ROOT': os.environ['BMAD_ROOT'],
        'KIRO_AGENTS_PATH': os.environ['KIRO_AGENTS_PATH'],
        'BMAD_WORKFLOWS_PATH': os.environ['BMAD_WORKFLOWS_PATH']
    }}

if __name__ == '__main__':
    env = setup_bmad_environment()
    for key, value in env.items():
        print(f"{{key}}={{value}}")
"""
    
    with open(init_module, 'w') as f:
        f.write(init_module_content)
    os.chmod(init_module, 0o755)
    print(f"✓ 创建 Python 初始化模块: {init_module}")
    
    # 5. 验证 bmad 结构
    print("\n📋 验证 bmad 结构:")
    bmad_modules = ['core', 'bmm', 'bmgd', 'cis', 'bmb']
    for module in bmad_modules:
        module_path = bmad_dir / module
        if module_path.exists():
            print(f"  ✓ {module}")
        else:
            print(f"  ✗ {module} (缺失)")
    
    print("\n✅ kiro-cli bmad 方法初始化完成!")
    print("\n📝 使用方法:")
    print("  1. 加载环境: source init_bmad.sh")
    print("  2. 或使用 Python: python3 bmad_kiro_init.py")
    print("  3. 然后运行: kiro-cli chat")
    
    return True

if __name__ == '__main__':
    success = init_bmad_kiro()
    sys.exit(0 if success else 1)
