# Ý tưởng sản phẩm: Hybrid Task/Notes MCP Server

## Bối cảnh

Trong quá trình học và làm việc với code, mình thường phải ghi nhanh các việc cần làm, ghi chú kỹ thuật, lỗi cần kiểm tra, hoặc ý tưởng phát sinh. Nếu làm thủ công, mình phải tự mở file, đặt tên file, nhớ format, thêm tag, rồi sau đó tự tìm lại.

Ý tưởng sản phẩm là xây một MCP Server cá nhân để AI client như Claude Code có thể giúp mình capture và tra cứu task/note trực tiếp.

## Công việc thực tế cần tự động hóa

Thay vì ghi task/note bằng tay vào file Markdown, người dùng có thể yêu cầu Claude Code:

- Lưu một task mới khi đang làm việc.
- Lưu một note ngắn về bug, quyết định kỹ thuật, hoặc ý tưởng.
- Liệt kê lại các task/note theo loại hoặc theo tag.
- Kiểm tra nhanh server còn hoạt động hay không.

## MCP Server đề xuất

Tên server: `tasks-notes`

Loại dữ liệu lưu trữ: Markdown files

Vị trí lưu dữ liệu dự kiến:

```text
data/items/*.md
```

Mỗi item là một file Markdown có frontmatter metadata:

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

## Tools cho Bài 1

### `capture_item`

Mục đích: tạo mới một task hoặc note.

Input:

| Field | Type | Required | Mô tả |
|---|---|---|---|
| `type` | string | yes | `task` hoặc `note` |
| `content` | string | yes | Nội dung cần lưu |
| `tags` | array/string | no | Danh sách tag, ví dụ `mcp`, `lab`, `bug` |

Output dự kiến:

```json
{
  "id": "task-20260828-153012",
  "type": "task",
  "status": "open",
  "tags": ["mcp", "lab"],
  "path": "data/items/task-20260828-153012.md"
}
```

### `list_items`

Mục đích: đọc lại danh sách task/note đã lưu.

Input:

| Field | Type | Required | Mô tả |
|---|---|---|---|
| `type` | string | no | Lọc theo `task` hoặc `note` |
| `tag` | string | no | Lọc theo tag |
| `limit` | integer | no | Số item tối đa trả về |

Output dự kiến:

```json
[
  {
    "id": "task-20260828-153012",
    "type": "task",
    "status": "open",
    "tags": ["mcp", "lab"],
    "content": "Hoàn thành MCP Server hybrid Task/Notes cho Day26 lab"
  }
]
```

## Hướng mở rộng cho Bài 2

Chuyển server từ `stdio` sang `streamable-http`.

Thêm bearer token auth:

- Token đúng: cho phép gọi tools.
- Token sai: từ chối bằng HTTP `401` hoặc `403`.
- Không có token: từ chối bằng HTTP `401`.

Luồng:

```text
Claude Code / MCP Client
        |
        | Authorization: Bearer <token>
        v
MCP Server
        |
        | TokenVerifier
        v
Task/Notes tools
```

## Hướng mở rộng cho Bài 3

Thêm versioning để client cũ không bị hỏng.

Chiến lược:

- Giữ tool v1: `capture_item`, `list_items`.
- Thêm tool v2: `capture_item_v2`, `list_items_v2`.
- v1 có thể trả text đơn giản.
- v2 trả JSON chi tiết hơn.
- Thêm resource `server://info`.

Metadata dự kiến từ `server://info`:

```json
{
  "name": "tasks-notes",
  "server_version": "2.0.0",
  "tools": {
    "capture_item": {
      "version": "1.0",
      "deprecated": false
    },
    "list_items": {
      "version": "1.0",
      "deprecated": true,
      "replacement": "list_items_v2"
    },
    "list_items_v2": {
      "version": "2.0",
      "deprecated": false
    }
  },
  "capabilities": ["markdown-storage", "tags", "filtering", "versioning"]
}
```

## Tiêu chí hoàn thành

- Có MCP Server tự xây phục vụ công việc ghi task/note cá nhân.
- Có ít nhất 2 tools hoạt động: `capture_item`, `list_items`.
- Dữ liệu trả về là kết quả thực tế từ file Markdown, không phải text hard-code.
- Có hướng dẫn đăng ký server vào Claude Code.
- Có client hoặc hướng dẫn test để chứng minh tool chạy được.
- Có kế hoạch nâng cấp auth và versioning cho các bài tiếp theo.
