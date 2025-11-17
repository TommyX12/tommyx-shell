from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from typing import Optional
import difflib
import json
from claude_agent_sdk import query, ClaudeAgentOptions, ClaudeSDKClient, PermissionResultAllow, PermissionResultDeny

openai_client = OpenAI()

class LLMConfig(BaseModel):
    model: str = "gpt-5.1"
    rate_limit_fallback_model: str = "gpt-5"

    reasoning_effort: str = "low"

    class Config:
        frozen = True

def call_llm(input: list[dict] | str, response_format: Optional[BaseModel] = None, config: LLMConfig = LLMConfig()):
    if isinstance(input, str):
        input = [{"role": "user", "content": input}]

    args = {
        "model": config.model,
        "input": input,
        "reasoning": {
            "effort": config.reasoning_effort,
        },
    }

    def query(args: dict):
        if response_format:
            response = openai_client.responses.parse(
                **args,
                text_format=response_format,
            )
            return response.output_parsed
        else:
            response = openai_client.responses.create(**args)
            return response.output_text

    try:
        return query(args)
    except RateLimitError:
        print(f"Rate limit exceeded for model {config.model}, retrying with fallback model {config.rate_limit_fallback_model}")
        # Retry once with fallback model
        args["model"] = config.rate_limit_fallback_model
        return query(args)

class AgentConfig(BaseModel):
    permission_mode: str = "default"
    load_project_settings: bool = True
    load_user_settings: bool = True
    override_system_prompt: str | None = None

def visualize_diff(old_string: str, new_string: str, file_path: str = ""):
    """Visualize line-based and character-based diff between two strings."""
    old_lines = old_string.splitlines(keepends=True)
    new_lines = new_string.splitlines(keepends=True)
    
    # Line-based unified diff
    print(f"\n   📝 Diff for {file_path if file_path else 'content'}:")
    print("   " + "=" * 70)
    
    # Unified diff format (like git diff)
    unified_diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"old: {file_path}" if file_path else "old",
        tofile=f"new: {file_path}" if file_path else "new",
        lineterm='',
        n=5  # context lines
    )
    
    for line in unified_diff:
        line = line.rstrip()
        if line.startswith('---') or line.startswith('+++'):
            print(f"   {line}")
        elif line.startswith('@@'):
            print(f"   {line}")
        elif line.startswith('-'):
            print(f"   \033[91m{line}\033[0m")  # Red for deletions
        elif line.startswith('+'):
            print(f"   \033[92m{line}\033[0m")  # Green for additions
        elif line.startswith(' '):
            print(f"   {line}")
    
    print("   " + "=" * 70)

async def run_agent(cwd: str, prompt: str, config: AgentConfig = AgentConfig()):
    async def prompt_for_tool_approval(tool_name: str, input_params: dict, context: dict):
        print(f"\n🔧 Tool Request:")
        print(f"   Tool: {tool_name}")

        original_input_params = input_params

        # Special handling for Edit tool
        if tool_name == "Edit" and "old_string" in input_params and "new_string" in input_params:
            file_path = input_params.get("file_path", "")
            old_string = input_params["old_string"]
            new_string = input_params["new_string"]
            
            visualize_diff(old_string, new_string, file_path)
            
            # Still show other parameters if any
            input_params = {k: v for k, v in input_params.items() if k not in ["old_string", "new_string", "file_path"]}

        if input_params:
            print("   Parameters:")
            for key, value in input_params.items():
                display_value = value
                if isinstance(value, str) and len(value) > 100:
                    display_value = value[:100] + "..."
                elif isinstance(value, (dict, list)):
                    display_value = json.dumps(value, indent=2)
                print(f"     {key}: {display_value}")

        # Get user approval
        answer = input("\n   Approve this tool use? (y/explain): ")

        if answer.lower() == 'y':
            print("   ✅ Approved\n")
            return PermissionResultAllow(
                behavior="allow",
                updated_input=original_input_params
            )
        else:
            print("   ❌ Denied\n")
            return PermissionResultDeny(
                behavior="deny",
                message=answer
            )

    setting_sources = []
    if config.load_project_settings:
        setting_sources.append("project")
    if config.load_user_settings:
        setting_sources.append("user")
    
    system_prompt = config.override_system_prompt
    if system_prompt is None:
        system_prompt = {
            "type": "preset",
            "preset": "claude_code"  # Use Claude Code's system prompt
        }

    options = ClaudeAgentOptions(
        permission_mode=config.permission_mode,
        cwd=cwd,
        system_prompt=system_prompt,
        setting_sources=setting_sources,
        can_use_tool=prompt_for_tool_approval,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            # TODO: print nicely
            print(message)