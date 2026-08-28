"""Bài 1 — `tasks-notes` MCP Server (transport: stdio).

3 tool: `capture_item`, `list_items`, `ping`.
Dữ liệu lưu / đọc từ file Markdown trong `data/items/` (xem `store.py`).

Chạy trực tiếp (client tự khởi động qua stdio):
    python server.py

Đăng ký vào Claude Code (đường dẫn tuyệt đối):
    claude mcp add tasks-notes -- python <ABS_PATH>/05-tasks-notes/server.py
"""
from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

import store


def register_core_tools(mcp: MCPServer) -> None:
    """Gắn 3 tool lõi vào 1 MCPServer bất kỳ (được Bài 2 tái sử dụng)."""

    @mcp.tool()
    def capture_item(
        type: str,
        content: str,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Tạo mới một task hoặc note và lưu thành file Markdown.

        Args:
            type: "task" hoặc "note".
            content: Nội dung cần lưu.
            tags: Danh sách tag, ví dụ ["mcp", "lab"]. Có thể bỏ trống.
        """
        return store.create_item(type, content, tags)

    @mcp.tool()
    def list_items(
        type: str | None = None,
        tag: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Đọc lại danh sách task/note đã lưu (đọc thật từ file Markdown).

        Args:
            type: Lọc theo "task" hoặc "note". Bỏ trống = tất cả.
            tag: Chỉ lấy item có tag này.
            limit: Số item tối đa trả về.
        """
        return store.read_items(type, tag, limit)

    @mcp.tool()
    def ping() -> str:
        """Kiểm tra server còn sống."""
        return "pong — tasks-notes MCP server is alive"


mcp = MCPServer("tasks-notes")
register_core_tools(mcp)


if __name__ == "__main__":
    mcp.run()
