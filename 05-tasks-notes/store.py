"""Lõi lưu trữ dùng chung cho cả 3 bài lab `tasks-notes`.

Mọi item = 1 file Markdown có frontmatter trong `data/items/*.md`.
Không dùng thư viện YAML ngoài để giữ lab gọn — parse/ghi frontmatter thủ công.
Các server (`server.py`, `server_http.py`, `server_v2.py`) chỉ bọc các hàm ở đây
thành MCP tool; toàn bộ dữ liệu trả về đều đọc THẬT từ file, không hard-code.
"""
from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
ITEMS_DIR = BASE_DIR / "data" / "items"
TZ = datetime.timezone(datetime.timedelta(hours=7))  # +07:00


def _ensure_dir() -> None:
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> datetime.datetime:
    return datetime.datetime.now(TZ).replace(microsecond=0)


def normalize_tags(tags: Any) -> list[str]:
    """Chấp nhận list (`["mcp", "lab"]`) hoặc chuỗi CSV (`"mcp, lab"`)."""
    if tags is None:
        return []
    raw: list[str] = []
    if isinstance(tags, str):
        raw = re.split(r"[,\s]+", tags.strip())
    else:
        for t in tags:
            raw.extend(re.split(r"[,\s]+", str(t).strip()))
    seen: list[str] = []
    for t in (x.strip() for x in raw):
        if t and t not in seen:
            seen.append(t)
    return seen


def _new_id(type_: str, now: datetime.datetime) -> str:
    base = f"{type_}-{now.strftime('%Y%m%d-%H%M%S')}"
    cand, n = base, 1
    while (ITEMS_DIR / f"{cand}.md").exists():
        n += 1
        cand = f"{base}-{n}"
    return cand


def create_item(type_: str, content: str, tags: Any = None) -> dict[str, Any]:
    """Tạo mới 1 task/note, ghi ra file Markdown, trả metadata."""
    if type_ not in ("task", "note"):
        raise ValueError("type phải là 'task' hoặc 'note'")
    if not content or not content.strip():
        raise ValueError("content là bắt buộc")

    _ensure_dir()
    now = _now()
    tag_list = normalize_tags(tags)
    item_id = _new_id(type_, now)
    status = "open" if type_ == "task" else "captured"

    frontmatter = (
        "---\n"
        f"id: {item_id}\n"
        f"type: {type_}\n"
        f"status: {status}\n"
        f"tags: [{', '.join(tag_list)}]\n"
        f"created_at: {now.isoformat()}\n"
        "version: 1\n"
        "---\n\n"
        f"{content.strip()}\n"
    )
    path = ITEMS_DIR / f"{item_id}.md"
    path.write_text(frontmatter, encoding="utf-8")

    return {
        "id": item_id,
        "type": type_,
        "status": status,
        "tags": tag_list,
        "created_at": now.isoformat(),
        "path": str(path.relative_to(BASE_DIR)).replace(os.sep, "/"),
    }


def _parse_file(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, Any] = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block = text[3:end].strip("\n")
            body = text[end + 4:].lstrip("\n")
            for line in block.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key, value = key.strip(), value.strip()
                if key == "tags":
                    value = value.strip("[]")
                    meta[key] = [t.strip() for t in value.split(",") if t.strip()]
                else:
                    meta[key] = value
    return meta, body.strip()


def read_items(
    type_: str | None = None,
    tag: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Đọc lại toàn bộ item từ `data/items/`, lọc theo type/tag, mới nhất trước."""
    _ensure_dir()
    rows: list[dict[str, Any]] = []
    for path in ITEMS_DIR.glob("*.md"):
        meta, body = _parse_file(path)
        if not meta:
            continue
        if type_ and meta.get("type") != type_:
            continue
        if tag and tag not in meta.get("tags", []):
            continue
        rows.append(
            {
                "id": meta.get("id", path.stem),
                "type": meta.get("type"),
                "status": meta.get("status"),
                "tags": meta.get("tags", []),
                "created_at": meta.get("created_at"),
                "content": body,
            }
        )

    rows.sort(key=lambda r: r.get("created_at") or "", reverse=True)
    if limit is not None:
        try:
            rows = rows[: int(limit)]
        except (TypeError, ValueError):
            pass
    return rows
