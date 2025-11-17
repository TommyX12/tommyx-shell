from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from typing import Optional
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

async def run_agent(cwd: str, prompt: str, config: AgentConfig = AgentConfig()):
    async def prompt_for_tool_approval(tool_name: str, input_params: dict, context: dict):
        print(f"\n🔧 Tool Request:")
        print(f"   Tool: {tool_name}")

        # Display parameters
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
                updated_input=input_params
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