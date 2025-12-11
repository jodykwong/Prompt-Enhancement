# 快速开始指南

5 分钟快速上手 Prompt Enhancement。

## 📦 第 1 步：安装（1 分钟）

选择一种安装方式：

### 选项 A：使用 pip（推荐）

```bash
pip install prompt-enhancement
prompt-enhance-install /path/to/your/project
```

### 选项 B：使用 NPM

```bash
npm install -g @jodykwong/prompt-enhancement
prompt-enhance-install /path/to/your/project
```

## 🔑 第 2 步：配置 API 密钥（2 分钟）

### 快速配置

```bash
prompt-enhance-setup
```

按提示操作：
1. 访问 https://platform.deepseek.com
2. 创建 API 密钥
3. 粘贴到提示中

### 或手动配置

```bash
# 编辑项目的 .env 文件
echo "DEEPSEEK_API_KEY=sk-your-api-key-here" > /path/to/project/.env
```

## ✔️ 第 3 步：验证（1 分钟）

```bash
prompt-enhance-verify
```

应该看到：

```
✅ .claude 目录
✅ .claude/commands 目录
✅ pe.md 命令
✅ enhance.py 脚本
✅ .env 文件
✅ DEEPSEEK_API_KEY
```

## 🚀 第 4 步：使用（1 分钟）

在 Claude Code 中输入：

```bash
/pe 修复登录页面的bug
```

系统将：
1. 📂 扫描您的项目结构
2. 🔍 分析技术栈
3. 🤖 用 AI 增强您的提示词
4. 📝 显示原始版本 vs 增强版本
5. 🎯 让您选择下一步

## 📚 示例用法

```bash
# 修复 bug
/pe 修复移动设备上登录页面的身份验证 bug

# 添加功能
/pe 添加用户资料导出功能，支持 CSV 和 JSON 格式

# 优化性能
/pe 优化数据库查询，p99 延迟 < 100ms，需要向后兼容

# 重构代码
/pe 在 src/auth/login.ts 中实现 MFA 支持

# 编写文档
/pe 为 API 端点写 OpenAPI 规范文档
```

## 🎯 工作流程

```
您输入                  AI 分析                   显示结果
/pe 提示词  →  [收集上下文] → [增强提示词] →  [比较对比]
              [技术栈]      [结构化步骤]     [菜单选择]
              [Git 历史]    [验收标准]
                           [错误处理]
                              ↓
您的选择: [使用] [修改] [重新增强] [拒绝]
```

## 📋 快速参考

### 命令

```bash
# 安装
prompt-enhance-install [path]

# 配置
prompt-enhance-setup

# 验证
prompt-enhance-verify

# 使用
/pe 您的提示词
```

### 在 Claude Code 中

```bash
# 查看帮助
/pe

# 增强提示词
/pe 您的提示词
```

## 🆘 遇到问题？

### /pe 命令找不到

```bash
# 重新安装
prompt-enhance-install /path/to/project

# 验证
prompt-enhance-verify
```

### API 密钥错误

```bash
# 重新配置
prompt-enhance-setup

# 或编辑 .env
cat /path/to/project/.env
```

### 需要帮助？

更详细的信息：
- [完整安装指南](./INSTALL.md)
- [故障排除](./TROUBLESHOOTING.md)
- [GitHub 项目](https://github.com/jodykwong/Prompt-Enhancement)

## ✅ 您已准备好！

现在您可以：

1. ✨ 在任何项目中使用 `/pe` 命令
2. 📝 增强您的提示词
3. 🚀 提高开发效率
4. 🎯 获得更好的 AI 协助

---

**需要在其他项目中安装？**

```bash
prompt-enhance-install /path/to/another/project
```

就是这样！祝您使用愉快！ 🎉
