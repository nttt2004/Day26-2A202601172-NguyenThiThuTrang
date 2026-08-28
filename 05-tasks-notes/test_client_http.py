"""Bài 2 — MCP client test qua Streamable HTTP + bearer token.

Cần server_http.py đang chạy ở terminal khác:
    python server_http.py

Rồi:
    python test_client_http.py

3 kịch bản:
    1. Token đúng   -> list_tools + capture_item + list_items OK
    2. Token sai    -> bị từ chối (HTTP 401)
    3. Thiếu token  -> bị từ chối (HTTP 401)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8090/mcp")
GOOD_TOKEN = os.getenv("TASKS_NOTES_TOKEN", "dev-token-abc123")


def _dump(result) -> str:
    if getattr(result, "structuredContent", None):
        return json.dumps(result.structuredContent, ensure_ascii=False, indent=2)
    return "\n".join(getattr(b, "text", str(b)) for b in result.content)


async def run_session(token: str | None) -> None:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers) as hc:
        async with streamable_http_client(URL, http_client=hc) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("  tools:", ", ".join(t.name for t in tools.tools))
                created = await session.call_tool("capture_item", {
                    "type": "note",
                    "content": "Note tạo qua HTTP (token đúng)",
                    "tags": ["mcp", "http"],
                })
                print("  capture_item ->", _dump(created))
                listed = await session.call_tool("list_items", {"limit": 3})
                print("  list_items ->", _dump(listed))


async def main() -> None:
    print("=== 1. Token đúng ===")
    try:
        await run_session(GOOD_TOKEN)
        print("  ✅ OK")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ Không mong đợi: {type(e).__name__}: {e}")

    print("\n=== 2. Token sai ===")
    try:
        await run_session("wrong-token-000")
        print("  ❌ Không mong đợi: server lẽ ra phải từ chối")
    except Exception as e:  # noqa: BLE001
        print(f"  ✅ Bị từ chối như mong đợi: {type(e).__name__}: {e}")

    print("\n=== 3. Thiếu token ===")
    try:
        await run_session(None)
        print("  ❌ Không mong đợi: server lẽ ra phải từ chối")
    except Exception as e:  # noqa: BLE001
        print(f"  ✅ Bị từ chối như mong đợi: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
