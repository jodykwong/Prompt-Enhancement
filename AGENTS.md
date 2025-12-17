# Repository Guidelines (项目准则)

## 1. 项目组织 (Project Structure)
- **/src**: 提示词增强逻辑核心代码
- **/config**: 配置文件
- **AGENTS.md**: 本指南文件
- **@bmad**: BMAD 自动化流程配置 (workflow.xml)

## 2. 开发命令 (Commands)
- **初始化环境**: `pip install -r requirements.txt` (如有)
- **运行增强逻辑**: `python main.py` 或 `codex ./src`
- **测试**: `pytest`

## 3. 提交规范 (Git Commits)
- 遵循 Angular 规范: `feat: 增加XX功能`, `fix: 修复XX问题`

## 4. Agent 执行逻辑 (Crucial)
- 启动后必须优先执行: `LOAD @bmad/core/tasks/workflow.xml`
- 执行配置文件: `bmad/bmm/workflows/workflow-status/workflow.yaml`
