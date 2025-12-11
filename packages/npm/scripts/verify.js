#!/usr/bin/env node

/**
 * Verification script for Prompt Enhancement
 * 检查安装状态和诊断问题
 */

import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const projectDir = process.cwd();
const claudeDir = path.join(projectDir, '.claude');
const commandsDir = path.join(claudeDir, 'commands');
const envFile = path.join(projectDir, '.env');

console.log('\n' + '='.repeat(70));
console.log(chalk.cyan.bold('✔️  Prompt Enhancement 检查'));
console.log('='.repeat(70));
console.log(chalk.white(`\n📂 项目目录: ${projectDir}\n`));

// 检查文件
console.log('文件检查清单:');
console.log('-'.repeat(70));

const fileChecks = {
  '.claude 目录': claudeDir,
  '.claude/commands 目录': commandsDir,
  'pe.md 命令': path.join(commandsDir, 'pe.md'),
  'enhance.py 脚本': path.join(commandsDir, 'scripts', 'enhance.py'),
  '.env 文件': envFile
};

let filesOk = true;

Object.entries(fileChecks).forEach(([name, filepath]) => {
  if (fs.existsSync(filepath)) {
    console.log(chalk.green(`  ✅ ${name.padEnd(30)} ${filepath}`));
  } else {
    console.log(chalk.red(`  ❌ ${name.padEnd(30)} ${filepath} (缺失)`));
    filesOk = false;
  }
});

// 检查环境变量
console.log('\n环境变量:');
console.log('-'.repeat(70));

const apiKey = process.env.DEEPSEEK_API_KEY;

if (apiKey) {
  const masked = apiKey.substring(0, 10) + '...' + apiKey.substring(apiKey.length - 4);
  console.log(chalk.green(`  ✅ DEEPSEEK_API_KEY (环境变量): ${masked}`));
} else {
  if (fs.existsSync(envFile)) {
    const content = fs.readFileSync(envFile, 'utf-8');
    if (content.includes('DEEPSEEK_API_KEY=')) {
      console.log(chalk.yellow(`  ⚠️  DEEPSEEK_API_KEY (.env 文件): 已设置但未加载`));
    } else {
      console.log(chalk.red(`  ❌ DEEPSEEK_API_KEY: 未配置`));
    }
  } else {
    console.log(chalk.red(`  ❌ DEEPSEEK_API_KEY: 未配置`));
  }
}

// 检查 Python 依赖
console.log('\nPython 依赖:');
console.log('-'.repeat(70));

const pythonDeps = ['openai', 'dotenv'];
let depsOk = true;

pythonDeps.forEach(dep => {
  try {
    execSync(`python3 -c "import ${dep.replace('-', '_')}"`, {
      stdio: 'pipe',
      timeout: 5000
    });
    console.log(chalk.green(`  ✅ ${dep}`));
  } catch (e) {
    console.log(chalk.yellow(`  ⚠️  ${dep} (可能未安装，但非必需)`));
  }
});

// 检查 Node.js 依赖
console.log('\nNode.js 依赖:');
console.log('-'.repeat(70));

const nodeDeps = ['chalk'];
let nodeOk = true;

nodeDeps.forEach(dep => {
  try {
    require.resolve(dep);
    console.log(chalk.green(`  ✅ ${dep}`));
  } catch (e) {
    console.log(chalk.yellow(`  ⚠️  ${dep} (可能未安装)`));
  }
});

// 总结
console.log('\n' + '='.repeat(70));

if (filesOk && (apiKey || fs.existsSync(envFile))) {
  console.log(chalk.green.bold('✅ 所有检查通过！/pe 命令已准备好使用'));
} else {
  console.log(chalk.yellow.bold('⚠️  有些检查失败，请修复以下问题：'));
  console.log('');
  if (!filesOk) {
    console.log(chalk.white('  1. 重新安装: prompt-enhance-install'));
  }
  if (!apiKey && !fs.existsSync(envFile)) {
    console.log(chalk.white('  2. 配置环境: prompt-enhance-setup'));
  }
}

console.log('='.repeat(70) + '\n');
