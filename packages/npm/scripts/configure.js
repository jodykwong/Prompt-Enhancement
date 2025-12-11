#!/usr/bin/env node

/**
 * Interactive setup script for Prompt Enhancement
 * 交互式配置 DeepSeek API 密钥
 */

import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

const projectDir = process.cwd();
const envFile = path.join(projectDir, '.env');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (prompt) => {
  return new Promise(resolve => {
    rl.question(prompt, answer => {
      resolve(answer);
    });
  });
};

async function setupConfiguration() {
  console.log('\n' + '='.repeat(70));
  console.log(chalk.cyan.bold('⚙️  Prompt Enhancement 配置向导'));
  console.log('='.repeat(70));
  console.log(chalk.white(`\n📂 项目目录: ${projectDir}`));
  console.log(chalk.white(`📄 配置文件: ${envFile}\n`));

  // 检查 .env
  if (fs.existsSync(envFile)) {
    console.log(chalk.green('✓ .env 文件已存在'));
  } else {
    console.log(chalk.yellow('⚠️  .env 文件不存在'));
  }

  // 配置 API 密钥
  console.log('\n' + '-'.repeat(70));
  console.log(chalk.cyan('🔑 DeepSeek API 密钥配置'));
  console.log('-'.repeat(70));

  console.log(chalk.white(`
请获取您的 API 密钥:
1. 访问 https://platform.deepseek.com
2. 登录或注册账户
3. 创建 API 密钥
4. 复制密钥
  `));

  const apiKey = await question(chalk.cyan('请输入您的 DeepSeek API 密钥 (留空跳过): '));

  if (apiKey.trim()) {
    try {
      let envContent = '';

      if (fs.existsSync(envFile)) {
        envContent = fs.readFileSync(envFile, 'utf-8');

        // 检查是否已存在 DEEPSEEK_API_KEY
        if (envContent.includes('DEEPSEEK_API_KEY=')) {
          // 替换现有的
          envContent = envContent.replace(
            /DEEPSEEK_API_KEY=.*/,
            `DEEPSEEK_API_KEY=${apiKey}`
          );
        } else {
          // 添加新的
          envContent += `\nDEEPSEEK_API_KEY=${apiKey}\n`;
        }
      } else {
        envContent = `# DeepSeek API 配置\nDEEPSEEK_API_KEY=${apiKey}\n`;
      }

      fs.writeFileSync(envFile, envContent);
      console.log(chalk.green(`\n✓ API 密钥已保存到 ${envFile}`));

      // 显示掩码的密钥
      const masked = apiKey.substring(0, 10) + '...' + apiKey.substring(apiKey.length - 4);
      console.log(chalk.green(`✓ 密钥: ${masked}`));
    } catch (e) {
      console.log(chalk.red(`\n❌ 无法保存 API 密钥: ${e.message}`));
    }
  } else {
    console.log(chalk.yellow('\n⏭️  跳过 API 密钥配置'));
    console.log(chalk.white('   您可以稍后手动编辑 .env 文件\n'));
  }

  // 总结
  console.log('\n' + '-'.repeat(70));
  console.log(chalk.green('✅ 配置完成！'));
  console.log('-'.repeat(70));

  console.log(chalk.white(`
📝 下一步:
  在 Claude Code 中输入:
  /pe 您的提示词

📚 了解更多:
  https://github.com/jodykwong/Prompt-Enhancement
  `));

  console.log('='.repeat(70) + '\n');

  rl.close();
}

setupConfiguration().catch(e => {
  console.error(chalk.red(`\n❌ 错误: ${e.message}`));
  process.exit(1);
});
