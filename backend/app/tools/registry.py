"""LangChain-shaped tool registry (name, description, args_schema, invoke)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


@dataclass
class Tool:
    name: str
    description: str
    args_schema: dict[str, Any]
    invoke: Callable[..., Awaitable[dict[str, Any]]]
    widget_path: str | None = None


@dataclass
class Registry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def openai_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.args_schema,
                },
            }
            for t in self.tools.values()
        ]

    async def call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        tool = self.tools[name]
        return await tool.invoke(**(args or {}))
