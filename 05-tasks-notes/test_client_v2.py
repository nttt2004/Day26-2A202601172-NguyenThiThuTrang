"""Bài 3 — MCP client test versioning (stdio). Client tự khởi động server_v2.py.

    cd 05-tasks-notes
    python test_client_v2.py

Kịch bản: đọc resource server://info -> list_tools -> gọi cả 4 tool (v1 + v2).
"""
from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _dump(result) -> str:
    if getattr(result, "structuredContent", None):
        return json.dumps(result.structuredContent, ensure_ascii=False, indent=2)
    return "\n".join(getattr(b, "text", str(b)) for b in result.content)


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["server_v2.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=== resource server://info ===")
            info = await session.read_resource("server://info")
            info_text = info.contents[0].text
            print(info_text)
            meta = json.loads(info_text)

            print("\n=== list_tools ===")
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.splitlines()[0]}")

            # Client mới: đọc info, thấy list_items deprecated -> chọn v2
            for name, spec in meta["tools"].items():
                if spec.get("deprecated"):
                    print(f"\n⚠️  '{name}' deprecated -> nên dùng '{spec.get('replacement')}'")

            print("\n=== [v1] capture_item ===")
            print(_dump(await session.call_tool("capture_item", {
                "type": "task", "content": "Client cũ vẫn gọi v1", "tags": ["v1"]})))

            print("\n=== [v1] list_items ===")
            print(_dump(await session.call_tool("list_items", {"limit": 5})))

            print("\n=== [v2] capture_item_v2 ===")
            print(_dump(await session.call_tool("capture_item_v2", {
                "type": "note", "content": "Client mới lấy JSON qua v2", "tags": ["v2", "mcp"]})))

            print("\n=== [v2] list_items_v2 (tag=v2) ===")
            print(_dump(await session.call_tool("list_items_v2", {"tag": "v2"})))


if __name__ == "__main__":
    asyncio.run(main())
