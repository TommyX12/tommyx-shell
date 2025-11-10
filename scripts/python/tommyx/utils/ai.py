from openai import OpenAI
from pydantic import BaseModel
from typing import Literal, Optional

openai_client = OpenAI()

class LLMConfig(BaseModel):
    model: str = "gpt-5"
    reasoning_effort: Literal["minimal", "low", "medium", "high"] = "minimal"

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

    if response_format:
        response = openai_client.responses.parse(
            **args,
            text_format=response_format,
        )
        return response.output_parsed
    else:
        response = openai_client.responses.create( **args)
        return response.output_text
