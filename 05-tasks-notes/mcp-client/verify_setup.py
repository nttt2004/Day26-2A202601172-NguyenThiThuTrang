#!/usr/bin/env python3
"""Kiểm tra nhanh setup của tasks-notes ADK client."""
import os
import sys
from pathlib import Path


def check_env() -> bool:
    print("🔍 .env ...")
    if not Path(".env").exists():
        print("❌ chưa có .env — copy từ .env.example")
        return False
    from dotenv import load_dotenv

    load_dotenv()
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        print("❌ GOOGLE_API_KEY chưa điền — https://aistudio.google.com/apikey")
        return False
    print(f"✅ GOOGLE_API_KEY ({key[:8]}...)")
    print(f"   GEMINI_MODEL   = {os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}")
    print(f"   MCP_SERVER_URL = {os.getenv('MCP_SERVER_URL', 'http://localhost:8090/mcp')}")
    print(f"   TASKS_NOTES_TOKEN set = {bool(os.getenv('TASKS_NOTES_TOKEN'))}")
    return True


def check_deps() -> bool:
    print("\n🔍 dependencies ...")
    ok = True
    for mod, name in [
        ("google.adk", "Google ADK"),
        ("mcp", "MCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]:
        try:
            __import__(mod)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} — chạy: uv sync")
            ok = False
    return ok


def check_agent() -> bool:
    print("\n🔍 import agent ...")
    try:
        import warnings

        warnings.filterwarnings("ignore")
        from tasks_notes_agent import root_agent

        print(f"✅ agent: {root_agent.name} (model={root_agent.model})")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"❌ {e}")
        return False


if __name__ == "__main__":
    results = [check_env(), check_deps(), check_agent()]
    print("\n" + "=" * 50)
    if all(results):
        print("✅ Sẵn sàng — chạy: uv run adk web")
        sys.exit(0)
    print("❌ Còn lỗi ở trên")
    sys.exit(1)
