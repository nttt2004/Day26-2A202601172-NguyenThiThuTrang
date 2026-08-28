"""Tasks-Notes Agent — Google ADK làm MCP Client tới server `tasks-notes`.

Kết nối tới `server_http.py` (Bài 2) qua Streamable HTTP + bearer token.
ADK tự khám phá tool (capture_item, list_items, ping) và cho Gemini gọi.

Biến môi trường (xem .env.example):
    GOOGLE_API_KEY      key Gemini (bắt buộc)
    GEMINI_MODEL        mặc định "gemini-2.5-flash"
    TASKS_NOTES_TOKEN   bearer token khớp với server_http.py
    MCP_SERVER_URL      mặc định http://localhost:8090/mcp
"""
import logging
import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8090/mcp")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TASKS_NOTES_TOKEN = os.getenv("TASKS_NOTES_TOKEN", "dev-token-abc123")

logger.info("🗒️  Khởi tạo tasks-notes agent")
logger.info(f"📡 MCP Server: {MCP_SERVER_URL}")

INSTRUCTION = (
    "Bạn là trợ lý ghi chú cá nhân. Khi người dùng muốn lưu việc cần làm hoặc "
    "ghi chú kỹ thuật, gọi tool `capture_item` (type='task' hoặc 'note'). "
    "Khi người dùng muốn xem lại, gọi `list_items` với bộ lọc type/tag phù hợp. "
    "Dùng `ping` để kiểm tra server. Luôn tóm tắt kết quả tool bằng tiếng Việt."
)

try:
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        headers={"Authorization": f"Bearer {TASKS_NOTES_TOKEN}"},
        timeout=30.0,
    )
    tasks_notes_tools = McpToolset(connection_params=connection_params)
    logger.info("✅ McpToolset tạo thành công")

    root_agent = Agent(
        name="tasks_notes_agent",
        model=GEMINI_MODEL,
        instruction=INSTRUCTION,
        tools=[tasks_notes_tools],
    )
    logger.info("✅ tasks_notes_agent sẵn sàng: capture_item, list_items, ping")

except Exception as e:  # noqa: BLE001
    logger.error(f"❌ Không kết nối được MCP server: {e}")
    import traceback

    traceback.print_exc()
    logger.warning("⚠️  Tạo agent fallback không có tool")
    root_agent = Agent(
        name="tasks_notes_agent",
        model=GEMINI_MODEL,
        instruction=INSTRUCTION,
    )
