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

> ⚠️ `google-adk` yêu cầu `mcp` **1.x**, còn các server của lab dùng `mcp` **2.x**.
> Vì vậy client chạy ở **venv riêng**; server chạy bằng python global.

```powershell
cd 05-tasks-notes\mcp-client
copy .env.example .env         # rồi điền GOOGLE_API_KEY thật

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "google-adk" "mcp<2" python-dotenv httpx
python verify_setup.py
```

## Chạy

```powershell
# terminal 1 — MCP server (từ 05-tasks-notes/, python global mcp 2.x)
python server_http.py

# terminal 2 — ADK web (venv của client)
cd 05-tasks-notes\mcp-client
.\.venv\Scripts\Activate.ps1
adk web
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
