"""Bài 2 — `tasks-notes` MCP Server qua Streamable HTTP + Bearer token auth.

- Cùng 3 tool như Bài 1 (import lại `register_core_tools` từ `server.py`).
- `StaticTokenVerifier` kiểm tra bearer token:
    token đúng  -> AccessToken(scopes=["items:read", "items:write"])
    token sai / thiếu -> HTTP 401 (client bị từ chối trước khi chạm tool).

Chạy:
    python server_http.py            # -> http://127.0.0.1:8090/mcp
Env:
    TASKS_NOTES_TOKEN   token dev hợp lệ (mặc định "dev-token-abc123")
    MCP_HTTP_HOST       mặc định 127.0.0.1
    MCP_HTTP_PORT       mặc định 8090
"""
from __future__ import annotations

import os

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from pydantic import AnyHttpUrl

from server import register_core_tools

HOST = os.getenv("MCP_HTTP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_HTTP_PORT", "8090"))
PUBLIC_URL = os.getenv("MCP_PUBLIC_URL", f"http://{HOST}:{PORT}")

DEV_TOKEN = os.getenv("TASKS_NOTES_TOKEN", "dev-token-abc123")

# token -> (client_id, scopes)
VALID_TOKENS: dict[str, tuple[str, list[str]]] = {
    DEV_TOKEN: ("dev-user", ["items:read", "items:write"]),
    "prod-key-xyz789": ("prod-service", ["items:read", "items:write"]),
}


class StaticTokenVerifier(TokenVerifier):
    """Kiểm tra token tĩnh — không biết gì về nội dung tool."""

    async def verify_token(self, token: str) -> AccessToken | None:
        entry = VALID_TOKENS.get(token)
        if entry is None:
            return None
        client_id, scopes = entry
        return AccessToken(token=token, client_id=client_id, scopes=scopes)


mcp = MCPServer(
    "tasks-notes",
    token_verifier=StaticTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(PUBLIC_URL),
        resource_server_url=AnyHttpUrl(f"{PUBLIC_URL}/mcp"),
        required_scopes=["items:read"],
    ),
)
register_core_tools(mcp)


if __name__ == "__main__":
    print(f"🚀 tasks-notes HTTP MCP server -> {PUBLIC_URL}/mcp")
    print(f"   token dev hợp lệ: {DEV_TOKEN}")
    mcp.run("streamable-http", host=HOST, port=PORT, streamable_http_path="/mcp")
