#!/usr/bin/env python3
"""
kiro-cli bmad 初始化模块
"""

import os
from pathlib import Path

def setup_bmad_environment():
    """设置 bmad 环境变量"""
    project_root = Path(__file__).parent
    
    os.environ['BMAD_ROOT'] = str(project_root / '_bmad')
    os.environ['KIRO_AGENTS_PATH'] = str(project_root / '.kiro' / 'agents')
    os.environ['BMAD_WORKFLOWS_PATH'] = str(project_root / '_bmad' / 'core' / 'workflows')
    
    return {
        'BMAD_ROOT': os.environ['BMAD_ROOT'],
        'KIRO_AGENTS_PATH': os.environ['KIRO_AGENTS_PATH'],
        'BMAD_WORKFLOWS_PATH': os.environ['BMAD_WORKFLOWS_PATH']
    }

if __name__ == '__main__':
    env = setup_bmad_environment()
    for key, value in env.items():
        print(f"{key}={value}")
