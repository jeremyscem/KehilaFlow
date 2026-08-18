from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
from typing import Any, get_args, get_origin

from sqlalchemy.orm import Session


@dataclass
class RegisteredTool:
    function: Callable[..., dict]
    schema: dict
    write: bool


TOOL_REGISTRY: dict[str, RegisteredTool] = {}


def python_type_to_json_schema(
    annotation: Any,
) -> dict:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation is str:
        return {"type": "string"}

    if annotation is int:
        return {"type": "integer"}

    if annotation is float:
        return {"type": "number"}

    if annotation is bool:
        return {"type": "boolean"}

    if origin is list:
        return {
            "type": "array",
        }

    if type(None) in args:
        real_types = [arg for arg in args if arg is not type(None)]

        if len(real_types) == 1:
            schema = python_type_to_json_schema(real_types[0])

            return {
                "anyOf": [
                    schema,
                    {"type": "null"},
                ]
            }

    return {"type": "string"}


def ai_tool(
    *,
    description: str,
    write: bool = False,
):
    def decorator(
        function: Callable[..., dict],
    ) -> Callable[..., dict]:
        function_signature = signature(function)

        properties = {}
        required = []

        for (
            name,
            parameter,
        ) in function_signature.parameters.items():
            if name == "session":
                continue

            properties[name] = python_type_to_json_schema(parameter.annotation)

            if parameter.default is parameter.empty:
                required.append(name)

        schema = {
            "name": function.__name__,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

        TOOL_REGISTRY[function.__name__] = RegisteredTool(
            function=function,
            schema=schema,
            write=write,
        )

        return function

    return decorator


def get_tool_schemas(
    allow_writes: bool = False,
) -> list[dict]:
    return [
        tool.schema
        for tool in TOOL_REGISTRY.values()
        if (allow_writes or not tool.write)
    ]


def get_registered_tool(
    name: str,
) -> RegisteredTool:
    tool = TOOL_REGISTRY.get(name)

    if tool is None:
        raise ValueError(f"Unknown AI tool: {name}")

    return tool


def execute_tool(
    name: str,
    tool_input: dict,
    session: Session,
    *,
    allow_writes: bool = False,
) -> dict:
    tool = get_registered_tool(name)

    if tool.write and not allow_writes:
        raise ValueError("Write tool execution requires explicit confirmation.")

    return tool.function(
        session=session,
        **tool_input,
    )
