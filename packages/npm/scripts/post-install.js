#!/usr/bin/env node

/**
 * Post-installation script for Prompt Enhancement NPM package
 *
 * 在 npm install 后自动运行，提示用户安装到项目
 */

import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n' + '='.repeat(70));
console.log(chalk.cyan.bold('🚀 Prompt Enhancement - Post-Installation'));
console.log('='.repeat(70));

console.log(chalk.white(`
✅ NPM package installed successfully!

📝 Next steps:

1️⃣  Install to your Claude Code project:
   $ prompt-enhance-install /path/to/your/project

   Or in current directory:
   $ prompt-enhance-install

2️⃣  Configure DeepSeek API key:
   $ prompt-enhance-setup

   Or manually edit .env:
   $ echo "DEEPSEEK_API_KEY=your-api-key" >> /path/to/project/.env

3️⃣  Verify installation:
   $ prompt-enhance-verify

📚 Documentation:
   https://github.com/jodykwong/Prompt-Enhancement

🔑 Get API key:
   https://platform.deepseek.com

`));

console.log('='.repeat(70) + '\n');
