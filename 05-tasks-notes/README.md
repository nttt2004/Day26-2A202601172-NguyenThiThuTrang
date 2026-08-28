# 05 — `tasks-notes` MCP Server (Bài 1)

MCP Server cá nhân để Claude Code (hoặc bất kỳ MCP client nào) **capture và tra
cứu task/note** trực tiếp, thay vì tự mở file, đặt tên, nhớ format Markdown.

## Kiến trúc

```
Claude Code / test_client.py
        |  stdio (JSON-RPC / MCP)
        v
   server.py  ──►  data/items/*.md   (mỗi item = 1 file Markdown + frontmatter)
```

Transport: **stdio** (Bài 2 sẽ chuyển sang `streamable-http` + bearer token).

## Tools

| Tool | Mục đích | Input |
|---|---|---|
| `capture_item` | Tạo mới task/note | `type` (`task`\|`note`, bắt buộc), `content` (bắt buộc), `tags` (list hoặc CSV, tuỳ chọn) |
| `list_items` | Đọc lại danh sách đã lưu | `type` (lọc), `tag` (lọc), `limit` (số lượng) |
| `ping` | Kiểm tra server còn sống | — |

Kết quả `list_items` được **đọc thật từ file Markdown** trong `data/items/`,
không hard-code.

### Định dạng file item

```markdown
---
id: task-20260828-153012
type: task
status: open
tags: [mcp, lab]
created_at: 2026-08-28T15:30:12+07:00
version: 1
---

Hoàn thành MCP Server hybrid Task/Notes cho Day26 lab
```

`id` = `<type>-<YYYYMMDD-HHMMSS>` (tự thêm hậu tố `-2`, `-3`… nếu trùng giây).

## Cài đặt

```bash
# từ thư mục gốc repo
pip install -r requirements.txt      # cần mcp[cli] >= 2.x
```

> Bản `mcp` đang dùng là 2.x nên server import `from mcp.server.mcpserver import MCPServer`
> (ở mcp 1.x tên cũ là `FastMCP`).

## Test nhanh (chứng minh tool chạy được)

```bash
cd 05-tasks-notes
python test_client.py
```

Client tự khởi động `server.py`, gọi `list_tools` tại runtime rồi lần lượt
`ping → capture_item(task) → capture_item(note) → list_items`. Sau khi chạy,
mở `data/items/` sẽ thấy các file `.md` mới được tạo.

## Đăng ký vào Claude Code

```bash
# dùng đường dẫn tuyệt đối tới server.py
claude mcp add tasks-notes -- python e:\Day26-2A202601172-NguyenThiThuTrang\05-tasks-notes\server.py

# kiểm tra
claude mcp list
```

Sau đó trong Claude Code có thể yêu cầu bằng ngôn ngữ tự nhiên, ví dụ:

- "Lưu task: viết README cho Day26, tag mcp lab" → gọi `capture_item`
- "Liệt kê các note có tag bug" → gọi `list_items`
- "Server tasks-notes còn sống không?" → gọi `ping`

Gỡ đăng ký: `claude mcp remove tasks-notes`.

---

## Bài 2 — Streamable HTTP + Bearer token auth

| File | Vai trò |
|---|---|
| `server_http.py` | Cùng 3 tool như Bài 1 nhưng chạy qua **Streamable HTTP** tại `http://localhost:8090/mcp`, có `StaticTokenVerifier` kiểm tra bearer token. Logic tool import lại nguyên từ `server.py`. |
| `test_client_http.py` | Chạy 3 kịch bản: token đúng / token sai / thiếu token. |

```
Claude Code / MCP Client
        |  Authorization: Bearer <token>
        v
   server_http.py ──► TokenVerifier.verify_token()
        |                token đúng → AccessToken(scopes=[items:read, items:write])
        |                token sai / thiếu → HTTP 401
        v
   capture_item / list_items / ping   (không biết gì về auth)
```

### Token hợp lệ (mặc định)

| Token | client_id |
|---|---|
| `dev-token-abc123` (đổi qua env `TASKS_NOTES_TOKEN`) | `dev-user` |
| `prod-key-xyz789` | `prod-service` |

### Chạy & test

```bash
cd 05-tasks-notes
python server_http.py            # terminal 1  → http://localhost:8090/mcp
python test_client_http.py       # terminal 2
```

Kết quả mong đợi:

```
=== Token đúng ===   → list_tools + capture_item + list_items OK
=== Token sai ===    → ❌ bị từ chối   (server log: POST /mcp 401 Unauthorized)
=== Thiếu token ===  → ❌ bị từ chối   (server log: POST /mcp 401 Unauthorized)
```

Kiểm tra nhanh bằng curl (thiếu token → 401):

```bash
curl -i -X POST http://localhost:8090/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Đăng ký bản HTTP vào Claude Code

```bash
claude mcp add --transport http tasks-notes-http http://localhost:8090/mcp \
  --header "Authorization: Bearer dev-token-abc123"
```

---

## Bài 3 — Versioning (client cũ không bị hỏng)

| File | Vai trò |
|---|---|
| `server_v2.py` | Server stdio giữ tool v1 + thêm tool v2 + resource `server://info`. Logic file tái sử dụng từ `server.py`. |
| `test_client_v2.py` | Đọc `server://info`, `list_tools`, gọi cả 4 tool. |

### Chiến lược

| Tool | Version | Deprecated | Kiểu trả về |
|---|---|---|---|
| `capture_item` | 1.0 | không | text ngắn: `Đã tạo task task-… #mcp → data/items/…md` |
| `list_items` | 1.0 | **có** → `list_items_v2` | text từng dòng |
| `capture_item_v2` | 2.0 | không | JSON đầy đủ metadata (`api_version`, `id`, `type`, `status`, `tags`, `path`) |
| `list_items_v2` | 2.0 | không | JSON gồm `filters` đã áp, `count`, mảng `items` chi tiết |

Client cũ vẫn gọi `capture_item` / `list_items` như Bài 1 và nhận text —
không vỡ. Client mới chuyển sang `*_v2` để lấy JSON.

### Resource `server://info`

```json
{
  "name": "tasks-notes",
  "server_version": "2.0.0",
  "tools": {
    "capture_item":    { "version": "1.0", "deprecated": false },
    "list_items":      { "version": "1.0", "deprecated": true, "replacement": "list_items_v2" },
    "capture_item_v2": { "version": "2.0", "deprecated": false },
    "list_items_v2":   { "version": "2.0", "deprecated": false }
  },
  "capabilities": ["markdown-storage", "tags", "filtering", "versioning"]
}
```

Client nên đọc resource này trước, kiểm tra `deprecated` rồi chọn tool phù hợp.

### Chạy & test

```bash
cd 05-tasks-notes
python test_client_v2.py     # tự khởi động server_v2.py
```

### Đăng ký vào Claude Code

```bash
claude mcp add tasks-notes-v2 -- python e:\Day26-2A202601172-NguyenThiThuTrang\05-tasks-notes\server_v2.py
```

## Bài 2b — ADK client (`mcp-client/`)

Agent Google ADK làm MCP Client tới `server_http.py`. Xem `mcp-client/README.md`.
Đổi so với 04-lab: package `weather_agent` → `tasks_notes_agent`, tool weather →
`tasks-notes`, thêm biến `GEMINI_MODEL`, `TASKS_NOTES_TOKEN`, `MCP_SERVER_URL`.

```powershell
cd 05-tasks-notes\mcp-client
copy .env.example .env    # điền GOOGLE_API_KEY
python -m venv .venv      # venv RIÊNG: google-adk cần mcp 1.x
.\.venv\Scripts\Activate.ps1
pip install "google-adk" "mcp<2" python-dotenv httpx
# (chạy server_http.py ở terminal khác, bằng python global)
adk web
```

## Ghi chú triển khai

- `mcp` cài trên máy là **2.x** → dùng `from mcp.server.mcpserver import MCPServer`
  (API còn lại `.tool()`, `.resource()`, `.run()` giữ nguyên như FastMCP 1.x).
- Logic lưu/đọc Markdown nằm ở `store.py`; 3 server chỉ bọc thành tool.
- Đường dẫn tuyệt đối trên máy này:
  `E:/Day26-2A202601172-NguyenThiThuTrang/05-tasks-notes/server.py`

## Tổng kết 3 bài

| Bài | File server | Transport | Điểm mới |
|---|---|---|---|
| 1 | `server.py` | stdio | `capture_item`, `list_items`, `ping` + lưu Markdown |
| 2 | `server_http.py` | streamable-http | Bearer token auth (401 khi sai/thiếu) |
| 3 | `server_v2.py` | stdio | v1 + v2 song song, resource `server://info` |
