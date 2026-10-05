from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import create_model, Field
from langchain_core.tools import StructuredTool
from mcp import Client

from src.config import get_settings

logger = logging.getLogger(__name__)


def python_type(schema: dict) -> Any:
    typ = schema.get("type")
    if typ == "string":
        return str
    if typ == "integer":
        return int
    if typ == "number":
        return float
    if typ == "boolean":
        return bool
    if typ == "array":
        return list
    if typ == "object":
        return dict
    return Any


def args_model(name: str, schema: dict):
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields = {}
    for field_name, field_schema in properties.items():
        annotation = python_type(field_schema)
        default = ... if field_name in required else field_schema.get("default", None)
        fields[field_name] = (annotation, Field(default=default, description=field_schema.get("description", "")))
    return create_model(f"{name.title().replace('_', '')}Args", **fields)


class MCPToolRegistry:
    def __init__(self) -> None:
        s = get_settings()
        self.urls = {
            "backend": s.backend_mcp_url,
            "rag": s.rag_mcp_url,
            "slack": s.slack_mcp_url,
            "jira": s.jira_mcp_url,
        }

    async def discover(self, server: str, allowlist: set[str] | None = None) -> list[StructuredTool]:
        url = self.urls[server]
        async with Client(url) as client:
            listed = await client.list_tools()

        tools = []
        for spec in listed.tools:
            if allowlist and spec.name not in allowlist:
                continue

            async def call_tool(_server=server, _name=spec.name, **kwargs):
                async with Client(self.urls[_server]) as client:
                    result = await client.call_tool(_name, kwargs)
                    if result.is_error:
                        raise RuntimeError(
                            f"MCP tool {_name} failed: {result.content}"
                        )
                    if result.structured_content:
                        return result.structured_content
                    text = []
                    for block in result.content:
                        if hasattr(block, "text"):
                            text.append(block.text)
                    return "\n".join(text)

            model = args_model(spec.name, spec.input_schema)
            tools.append(
                StructuredTool.from_function(
                    coroutine=call_tool,
                    name=spec.name,
                    description=spec.description or spec.name,
                    args_schema=model,
                )
            )
        return tools

    async def all_tools(self) -> list[StructuredTool]:
        groups = [
            await self.discover("backend"),
            await self.discover("rag"),
            await self.discover("slack"),
            await self.discover("jira"),
        ]
        return [tool for group in groups for tool in group]
