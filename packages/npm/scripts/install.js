#!/usr/bin/env node

/**
 * Main installation script for Prompt Enhancement
 *
 * Usage:
 *   prompt-enhance-install                    # Install to current directory
 *   prompt-enhance-install /path/to/project   # Install to specific project
 */

import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 获取目标项目路径
let targetProject = process.argv[2] || process.cwd();
targetProject = path.resolve(targetProject);

// 获取源项目路径（NPM 包的根目录 ../../）
const sourceRoot = path.resolve(__dirname, '../../..');

class Installer {
  constructor(targetProject, sourceRoot) {
    this.targetProject = targetProject;
    this.sourceRoot = sourceRoot;
    this.claudeDir = path.join(targetProject, '.claude');
    this.commandsDir = path.join(this.claudeDir, 'commands');
    this.hooksDir = path.join(this.claudeDir, 'hooks');
    this.scriptsDir = path.join(this.commandsDir, 'scripts');
  }

  log(message) {
    console.log(message);
  }

  error(message) {
    console.error(chalk.red(message));
  }

  success(message) {
    console.log(chalk.green(message));
  }

  info(message) {
    console.log(chalk.cyan(message));
  }

  validateTarget() {
    this.log('\n📂 验证目标项目...');

    if (!fs.existsSync(this.targetProject)) {
      this.error(`❌ 目标项目不存在: ${this.targetProject}`);
      process.exit(1);
    }

    // 检查是否看起来像一个项目
    const indicators = ['.git', 'src', 'package.json', 'setup.py', 'README.md'];
    const hasIndicator = indicators.some(ind =>
      fs.existsSync(path.join(this.targetProject, ind))
    );

    if (!hasIndicator) {
      this.log(chalk.yellow(`⚠️  警告: ${this.targetProject} 可能不是一个有效的项目目录`));
    }

    this.success(`   ✓ 项目路径有效: ${this.targetProject}`);
  }

  setupDirectories() {
    this.log('\n📁 设置目录结构...');

    [this.claudeDir, this.commandsDir, this.hooksDir, this.scriptsDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });

    this.success('   ✓ 创建目录: .claude/commands');
    this.success('   ✓ 创建目录: .claude/hooks');
  }

  installPeCommand() {
    this.log('\n📝 安装 /pe 命令...');

    const sourcePe = path.join(this.sourceRoot, '.claude/commands/pe.md');

    if (!fs.existsSync(sourcePe)) {
      this.error(`❌ 找不到源 /pe 命令: ${sourcePe}`);
      process.exit(1);
    }

    const targetPe = path.join(this.commandsDir, 'pe.md');

    try {
      // 尝试创建符号链接
      if (fs.existsSync(targetPe)) {
        fs.unlinkSync(targetPe);
      }

      try {
        fs.symlinkSync(sourcePe, targetPe);
        this.success(`   ✓ 创建符号链接: pe.md -> ${sourcePe}`);
      } catch (e) {
        // 如果符号链接失败，使用复制
        fs.copyFileSync(sourcePe, targetPe);
        this.log(chalk.yellow('   ℹ  使用文件复制（符号链接不支持）'));
        this.success(`   ✓ 复制文件: ${sourcePe}`);
      }
    } catch (e) {
      this.error(`❌ 无法安装 /pe 命令: ${e.message}`);
      process.exit(1);
    }
  }

  installSupportScripts() {
    this.log('\n🔧 安装支持脚本...');

    const sourceScripts = path.join(this.sourceRoot, '.claude/commands/scripts');

    if (fs.existsSync(sourceScripts)) {
      try {
        this.copyDirectory(sourceScripts, this.scriptsDir);
        this.success('   ✓ 复制脚本目录');
      } catch (e) {
        this.error(`⚠️  无法复制脚本目录: ${e.message}`);
      }
    }

    // 复制核心 Python 模块
    const coreModules = [
      'enhanced_prompt_generator.py',
      'async_prompt_enhancer.py',
      'context_collector.py'
    ];

    coreModules.forEach(module => {
      const sourceModule = path.join(this.sourceRoot, module);
      if (fs.existsSync(sourceModule)) {
        try {
          fs.copyFileSync(sourceModule, path.join(this.commandsDir, module));
          this.success(`   ✓ 复制模块: ${module}`);
        } catch (e) {
          this.log(chalk.yellow(`   ⚠️  跳过: ${module}`));
        }
      }
    });
  }

  setupEnvironment() {
    this.log('\n🔑 配置环境变量...');

    const envFile = path.join(this.targetProject, '.env');
    const envExample = path.join(this.sourceRoot, '.env.example');

    if (!fs.existsSync(envFile)) {
      let envContent = '# DeepSeek API 配置\nDEEPSEEK_API_KEY=your_api_key_here\n';

      if (fs.existsSync(envExample)) {
        envContent = fs.readFileSync(envExample, 'utf-8');
      }

      fs.writeFileSync(envFile, envContent);
      this.success(`   ✓ 创建 .env 文件`);
    } else {
      this.log('   ✓ .env 文件已存在');
    }
  }

  verify() {
    this.log('\n✔️  验证安装...');

    const checks = {
      'pe.md': path.join(this.commandsDir, 'pe.md'),
      'enhance.py': path.join(this.scriptsDir, 'enhance.py'),
      '.env': path.join(this.targetProject, '.env')
    };

    let allPassed = true;
    Object.entries(checks).forEach(([name, filepath]) => {
      if (fs.existsSync(filepath)) {
        this.success(`   ✓ ${name}`);
      } else {
        this.log(chalk.yellow(`   ⚠️  ${name} (未找到)`));
        allPassed = false;
      }
    });

    return allPassed;
  }

  copyDirectory(src, dest) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }

    const files = fs.readdirSync(src);
    files.forEach(file => {
      const srcPath = path.join(src, file);
      const destPath = path.join(dest, file);

      if (fs.statSync(srcPath).isDirectory()) {
        this.copyDirectory(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    });
  }

  install() {
    console.log('\n' + '='.repeat(70));
    console.log(chalk.cyan.bold('🚀 Prompt Enhancement 安装程序'));
    console.log('='.repeat(70));
    console.log(chalk.white(`📂 目标项目: ${this.targetProject}\n`));

    try {
      this.validateTarget();
      this.setupDirectories();
      this.installPeCommand();
      this.installSupportScripts();
      this.setupEnvironment();
      const verified = this.verify();

      console.log('\n' + '='.repeat(70));
      if (verified) {
        this.success('✅ 安装完成！');
      } else {
        this.log(chalk.yellow('⚠️  安装完成，但有些文件缺失'));
      }
      console.log('='.repeat(70));

      console.log(chalk.white(`
📝 后续步骤：

1️⃣  配置 DeepSeek API 密钥:
   $ prompt-enhance-setup

   或者编辑:
   ${path.join(this.targetProject, '.env')}

2️⃣  测试功能:
   在 Claude Code 中输入:
   /pe 修复登录页面的bug

3️⃣  获取更多帮助:
   https://github.com/jodykwong/Prompt-Enhancement
      `));

      console.log('='.repeat(70) + '\n');

    } catch (e) {
      this.error(`\n❌ 安装失败: ${e.message}`);
      console.log('='.repeat(70) + '\n');
      process.exit(1);
    }
  }
}

// 执行安装
const installer = new Installer(targetProject, sourceRoot);
installer.install();
