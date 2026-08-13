import json
import os

import anthropic
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import kehilaflow.ai.tools  # noqa: F401
from kehilaflow.ai.registry import (
    execute_tool,
    get_tool_schemas,
)

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


SYSTEM_PROMPT = """
You are the KehilaFlow admin assistant.

KehilaFlow manages donors, pledges, donations and campaigns.

Use the available tools whenever a question depends on KehilaFlow data.

Never invent financial data.

If the admin mentions a donor by name and you do not know their ID,
use search_donors first.

Keep answers concise and practical.

Amounts are in Israeli shekels (₪).
"""


def ask_claude(
    message: str,
    session: Session,
    allow_writes: bool = False,
) -> str:
    tools = get_tool_schemas(allow_writes=allow_writes)

    messages = [
        {
            "role": "user",
            "content": message,
        }
    ]

    for _ in range(10):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if not tool_calls:
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        tool_results = []

        for tool_call in tool_calls:
            try:
                result = execute_tool(
                    name=tool_call.name,
                    tool_input=tool_call.input,
                    session=session,
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(
                            result,
                            ensure_ascii=False,
                        ),
                    }
                )

            except (ValueError, KeyError) as error:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "is_error": True,
                        "content": str(error),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

    return "The AI assistant reached its tool-call limit."
