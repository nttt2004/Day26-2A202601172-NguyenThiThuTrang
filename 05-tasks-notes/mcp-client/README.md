# tasks-notes Agent — Google ADK MCP Client

Agent ADK làm **MCP Client** tới server `tasks-notes` (Bài 2, Streamable HTTP +
bearer token). ADK tự khám phá tool và cho Gemini gọi — không phải viết vòng
lặp function calling thủ công.

```
Browser :8000 ──> adk web ──> tasks_notes_agent (Gemini)
                                     │ Streamable HTTP + Bearer token
                                     ▼
                          server_http.py  :8090/mcp
                                     │
                                     ▼
                          data/items/*.md
```

## Setup

```bash
cd 05-tasks-notes/mcp-client
cp .env.example .env          # rồi điền GOOGLE_API_KEY thật
uv sync                       # hoặc: pip install -e .
python verify_setup.py
```

## Chạy

```bash
# terminal 1 — MCP server (từ 05-tasks-notes/)
python server_http.py

# terminal 2 — ADK web
cd mcp-client
uv run adk web
```

Mở http://localhost:8000, chọn `tasks_notes_agent`, thử:

- "Lưu task: viết README cho Day26, tag mcp lab"
- "Liệt kê các note có tag bug"
- "Server tasks-notes còn sống không?"

## Biến môi trường

| Biến | Mô tả |
|---|---|
| `GOOGLE_API_KEY` | Key Gemini — https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | Mặc định `gemini-2.5-flash` |
| `TASKS_NOTES_TOKEN` | Bearer token, phải khớp `server_http.py` |
| `MCP_SERVER_URL` | Mặc định `http://localhost:8090/mcp` |
