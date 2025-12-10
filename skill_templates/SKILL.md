---
name: prompt-enhancement
description: Enhance user prompts using DeepSeek API to make them more detailed, structured, and effective. Use this skill when the user wants to improve their prompt before executing a task, or when they explicitly ask to enhance/improve/expand their prompt.
allowed-tools: "Bash(python:*), Read"
version: 1.0.0
---

# Prompt Enhancement Skill

## Purpose

This skill enhances user prompts by calling the DeepSeek API to expand simple prompts into detailed, structured, and actionable instructions. It transforms brief requests into comprehensive task descriptions that lead to better results.

## When to Use

Use this skill when:
- User explicitly asks to enhance, improve, or expand their prompt
- User uses the `/pe` command followed by a prompt
- User says "enhance this prompt" or similar phrases
- The user's prompt is too brief or vague and could benefit from expansion

## How It Works

1. Takes the user's original prompt
2. Calls the DeepSeek API to generate an enhanced version
3. Returns a detailed, structured prompt with:
   - Clear step-by-step instructions
   - Specific technical details
   - Best practices and considerations
   - Expected outcomes

## Instructions

### Step 1: Identify the Prompt to Enhance

When the user wants to enhance a prompt, extract the prompt text from their request.

Examples:
- `/pe 修复登录页面的 bug` → prompt is "修复登录页面的 bug"
- "enhance this prompt: add user authentication" → prompt is "add user authentication"
- "请先增强这个提示词：优化数据库查询" → prompt is "优化数据库查询"

### Step 2: Run the Enhancement Script

Execute the enhancement script with the user's prompt:

```bash
python {baseDir}/scripts/enhance.py "<user_prompt>"
```

**Important Notes**:
- Replace `<user_prompt>` with the actual prompt text
- Use quotes to handle prompts with spaces
- The script will take 30-60 seconds to complete (DeepSeek API call)
- The script outputs the enhanced prompt to stdout

**Example**:
```bash
python {baseDir}/scripts/enhance.py "修复登录页面的 bug"
```

### Step 3: Handle the Output

The script will output the enhanced prompt directly to stdout. Read this output and present it to the user.

**Expected output format**:
```
1. **定位登录页面文件：** 检查前端登录页面组件...
2. **检查登录逻辑：** 审查登录表单的提交逻辑...
3. **验证错误处理：** 确保登录失败时有适当的错误提示...
...
```

### Step 4: Use the Enhanced Prompt

After presenting the enhanced prompt to the user, ask if they want to proceed with the task using the enhanced version.

If the user confirms, use the enhanced prompt to complete their original request.

## Error Handling

### If the script fails:

1. **Check the error message** in stderr
2. **Common errors**:
   - `DEEPSEEK_API_KEY not set`: User needs to set the API key environment variable
   - `No prompt provided`: The prompt argument was missing
   - `API call failed`: Network issue or API error

3. **Inform the user** about the error and suggest solutions:
   - For missing API key: "Please set your DEEPSEEK_API_KEY environment variable"
   - For network errors: "Unable to connect to DeepSeek API. Please check your internet connection"
   - For other errors: Show the error message and suggest trying again

### If the script takes too long:

- Inform the user: "Enhancing your prompt... This may take 30-60 seconds."
- If it exceeds 60 seconds, there may be a timeout issue

## Output Format

Present the enhanced prompt clearly to the user:

```
✅ **Enhanced Prompt**:

[Enhanced prompt content here]

---

Would you like me to proceed with this enhanced prompt?
```

## Examples

### Example 1: Simple Bug Fix

**User input**: `/pe 修复登录页面的 bug`

**Your actions**:
1. Run: `python {baseDir}/scripts/enhance.py "修复登录页面的 bug"`
2. Wait for output (30-60 seconds)
3. Present enhanced prompt to user
4. Ask if they want to proceed

### Example 2: Feature Request

**User input**: "enhance this prompt: add user authentication"

**Your actions**:
1. Extract prompt: "add user authentication"
2. Run: `python {baseDir}/scripts/enhance.py "add user authentication"`
3. Present enhanced prompt
4. Proceed with implementation if user confirms

### Example 3: Natural Language

**User input**: "请先增强这个提示词再执行：优化数据库查询"

**Your actions**:
1. Extract prompt: "优化数据库查询"
2. Run: `python {baseDir}/scripts/enhance.py "优化数据库查询"`
3. Present enhanced prompt
4. Execute the optimization task with enhanced prompt

## Technical Details

- **Script location**: `{baseDir}/scripts/enhance.py`
- **API**: DeepSeek API (deepseek-reasoner model)
- **Timeout**: 60 seconds
- **Output**: Enhanced prompt text to stdout
- **Errors**: Error messages to stderr

## Prerequisites

- Python 3.8+ installed
- DEEPSEEK_API_KEY environment variable set
- Required Python packages: openai, python-dotenv
- Internet connection for API access

## Notes

- The enhancement process uses AI and may produce different results each time
- Enhanced prompts are typically 10-50x longer than the original
- The script uses async processing for better performance
- Progress is not shown during execution (silent mode for Claude Code integration)

