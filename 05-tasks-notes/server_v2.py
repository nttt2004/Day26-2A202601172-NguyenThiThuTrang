"""Bài 3 — `tasks-notes` MCP Server có versioning (transport: stdio).

Giữ tool v1 (client cũ không vỡ) + thêm tool v2 (JSON chi tiết) + resource
`server://info` để client tự quyết định dùng tool nào.

| Tool             | Version | Deprecated | Trả về |
|------------------|---------|------------|--------|
| capture_item     | 1.0     | không      | text ngắn |
| list_items       | 1.0     | CÓ -> list_items_v2 | text từng dòng |
| capture_item_v2  | 2.0     | không      | JSON đầy đủ metadata |
| list_items_v2    | 2.0     | không      | JSON: filters + count + items |

Logic file tái sử dụng từ `store.py`.

    python test_client_v2.py        # tự khởi động file này
"""
from __future__ import annotations

import json
from typing import Any

from mcp.server.mcpserver import MCPServer

import store

SERVER_VERSION = "2.0.0"

SERVER_INFO: dict[str, Any] = {
    "name": "tasks-notes",
    "server_version": SERVER_VERSION,
    "tools": {
        "capture_item": {"version": "1.0", "deprecated": False},
        "list_items": {"version": "1.0", "deprecated": True, "replacement": "list_items_v2"},
        "capture_item_v2": {"version": "2.0", "deprecated": False},
        "list_items_v2": {"version": "2.0", "deprecated": False},
    },
    "capabilities": ["markdown-storage", "tags", "filtering", "versioning"],
}

mcp = MCPServer("tasks-notes", version=SERVER_VERSION)


# ---------------------------------------------------------------- v1 (giữ nguyên)
@mcp.tool()
def capture_item(type: str, content: str, tags: list[str] | None = None) -> str:
    """[v1.0] Tạo task/note. Trả text ngắn."""
    item = store.create_item(type, content, tags)
    tag_str = " ".join(f"#{t}" for t in item["tags"])
    return f"Đã tạo {item['type']} {item['id']} {tag_str} → {item['path']}".strip()


@mcp.tool()
def list_items(type: str | None = None, tag: str | None = None, limit: int | None = None) -> str:
    """[v1.0 - DEPRECATED, dùng list_items_v2] Liệt kê task/note, trả text từng dòng."""
    rows = store.read_items(type, tag, limit)
    if not rows:
        return "(chưa có item nào)"
    return "\n".join(
        f"- [{r['type']}] {r['id']} ({r['status']}) "
        f"{' '.join('#' + t for t in r['tags'])}  {r['content'][:60]}"
        for r in rows
    )


# ---------------------------------------------------------------------------- v2
@mcp.tool()
def capture_item_v2(type: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
    """[v2.0] Tạo task/note. Trả JSON đầy đủ metadata."""
    item = store.create_item(type, content, tags)
    return {"api_version": "2.0", **item}


@mcp.tool()
def list_items_v2(
    type: str | None = None,
    tag: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """[v2.0] Liệt kê task/note. Trả JSON gồm filters đã áp, count, mảng items chi tiết."""
    rows = store.read_items(type, tag, limit)
    return {
        "api_version": "2.0",
        "filters": {"type": type, "tag": tag, "limit": limit},
        "count": len(rows),
        "items": rows,
    }


@mcp.tool()
def ping() -> str:
    """Kiểm tra server còn sống."""
    return f"pong — tasks-notes v{SERVER_VERSION}"


@mcp.resource("server://info", mime_type="application/json")
def server_info() -> str:
    """Metadata versioning: tool nào deprecated, thay thế bằng gì."""
    return json.dumps(SERVER_INFO, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
