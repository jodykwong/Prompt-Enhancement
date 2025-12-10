#!/usr/bin/env python3
"""
Prompt Enhancement Script for Claude Code Skill

This script enhances user prompts by calling the DeepSeek API.
It's designed to be called by Claude Code through the Bash tool.

Usage:
    python enhance.py "<prompt_text>"

Environment Variables:
    DEEPSEEK_API_KEY: Required. Your DeepSeek API key.

Output:
    stdout: Enhanced prompt text
    stderr: Error messages (if any)
    exit code: 0 on success, 1 on error
"""

import sys
import os
import asyncio
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv is not installed", file=sys.stderr)
    print("Please install it: pip install python-dotenv", file=sys.stderr)
    sys.exit(1)

# Add the Prompt-Enhancement project to Python path
# This assumes the project is at ~/Documents/augment-projects/Prompt-Enhancement
PROJECT_ROOT = Path.home() / "Documents" / "augment-projects" / "Prompt-Enhancement"

if PROJECT_ROOT.exists():
    sys.path.insert(0, str(PROJECT_ROOT))
else:
    # Try alternative locations
    alternative_paths = [
        Path.home() / "Projects" / "Prompt-Enhancement",
        Path.home() / "prompt-enhancement",
        Path("/Users/jodykwong/Documents/augment-projects/Prompt-Enhancement"),
    ]

    for path in alternative_paths:
        if path.exists():
            PROJECT_ROOT = path
            sys.path.insert(0, str(PROJECT_ROOT))
            break
    else:
        print("Error: Cannot find Prompt-Enhancement project", file=sys.stderr)
        print(f"Searched locations:", file=sys.stderr)
        print(f"  - {PROJECT_ROOT}", file=sys.stderr)
        for path in alternative_paths:
            print(f"  - {path}", file=sys.stderr)
        sys.exit(1)

# Load .env file from project root
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    # Try to load from current directory as fallback
    load_dotenv()

try:
    from async_prompt_enhancer import AsyncPromptEnhancer
except ImportError as e:
    print(f"Error: Cannot import AsyncPromptEnhancer: {e}", file=sys.stderr)
    print(f"Project root: {PROJECT_ROOT}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)


def validate_environment():
    """Validate that required environment variables are set."""
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("Error: DEEPSEEK_API_KEY environment variable is not set", file=sys.stderr)
        print("", file=sys.stderr)
        print("The script tried to load the API key from:", file=sys.stderr)
        print(f"  1. .env file: {PROJECT_ROOT / '.env'}", file=sys.stderr)
        print(f"  2. Environment variables", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please add your API key to the .env file:", file=sys.stderr)
        print(f"  echo 'DEEPSEEK_API_KEY=your-api-key-here' >> {PROJECT_ROOT / '.env'}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or set it as an environment variable:", file=sys.stderr)
        print("  export DEEPSEEK_API_KEY='your-api-key-here'", file=sys.stderr)
        return False

    return True


def parse_arguments():
    """Parse command line arguments."""
    if len(sys.argv) < 2:
        print("Error: No prompt provided", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  python enhance.py \"<prompt_text>\"", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python enhance.py \"修复登录页面的 bug\"", file=sys.stderr)
        return None
    
    # Join all arguments to handle prompts with spaces
    prompt = " ".join(sys.argv[1:])
    
    if not prompt.strip():
        print("Error: Prompt is empty", file=sys.stderr)
        return None
    
    return prompt.strip()


async def enhance_prompt(prompt: str) -> dict:
    """
    Enhance the prompt using AsyncPromptEnhancer.
    
    Args:
        prompt: The original prompt text
        
    Returns:
        dict: Result dictionary from AsyncPromptEnhancer
    """
    try:
        enhancer = AsyncPromptEnhancer()
        
        # Call enhance with timeout (no progress callback for silent mode)
        result = await enhancer.enhance(
            original_prompt=prompt,
            timeout=60,
            progress_callback=None,  # Silent mode for Claude Code
            cancel_token=None
        )
        
        return result
        
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "API call timed out after 60 seconds",
            "original": prompt,
            "enhanced": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "original": prompt,
            "enhanced": None
        }


async def main():
    """Main entry point."""
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Parse arguments
    prompt = parse_arguments()
    if prompt is None:
        sys.exit(1)
    
    # Enhance the prompt
    result = await enhance_prompt(prompt)
    
    # Handle result
    if result['success']:
        # Output enhanced prompt to stdout
        print(result['enhanced'])
        sys.exit(0)
    else:
        # Output error to stderr
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

