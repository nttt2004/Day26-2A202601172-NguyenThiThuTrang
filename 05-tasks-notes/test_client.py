"""Bài 1 — MCP client test (stdio). Client tự khởi động server.py.

Không cần mạng, không cần secret.

    cd 05-tasks-notes
    python test_client.py

Kịch bản: list_tools -> ping -> capture_item(task) -> capture_item(note) -> list_items.
Sau khi chạy, mở data/items/ sẽ thấy các file .md mới.
"""
from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:  # console Windows mặc định cp1252 -> ép UTF-8 để in tiếng Việt
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _dump(result) -> str:
    if getattr(result, "structuredContent", None):
        return json.dumps(result.structuredContent, ensure_ascii=False, indent=2)
    return "\n".join(getattr(b, "text", str(b)) for b in result.content)


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools server công bố (khám phá tại runtime):")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.splitlines()[0]}")

            print("\n[ping]")
            print(" ->", _dump(await session.call_tool("ping", {})))

            print("\n[capture_item] task")
            print(_dump(await session.call_tool("capture_item", {
                "type": "task",
                "content": "Hoàn thành MCP Server hybrid Task/Notes cho Day26 lab",
                "tags": ["mcp", "lab"],
            })))

            print("\n[capture_item] note")
            print(_dump(await session.call_tool("capture_item", {
                "type": "note",
                "content": "Nhớ: mcp 2.x đổi FastMCP -> MCPServer",
                "tags": ["mcp", "bug"],
            })))

            print("\n[list_items] tất cả")
            print(_dump(await session.call_tool("list_items", {})))

            print("\n[list_items] type=note tag=bug")
            print(_dump(await session.call_tool("list_items", {"type": "note", "tag": "bug"})))


if __name__ == "__main__":
    asyncio.run(main())
