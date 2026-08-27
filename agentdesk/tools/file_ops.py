from __future__ import annotations

from pathlib import Path

from langchain.tools import tool

from config import get_settings


def _resolve_workspace_path(relative_path: str) -> Path:
    settings = get_settings()
    workspace_root = settings.workspace_path
    target = (workspace_root / relative_path).resolve()
    if not str(target).startswith(str(workspace_root)):
        raise ValueError("Access denied: path must stay inside the workspace directory.")
    return target


@tool("read_workspace_file")
def read_workspace_file(relative_path: str) -> str:
    """Read a UTF-8 text file from the workspace directory using a relative path."""
    try:
        target = _resolve_workspace_path(relative_path)
        if not target.exists():
            return f"File not found: {relative_path}"
        if not target.is_file():
            return f"Not a file: {relative_path}"
        return target.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return f"Read error: {exc}"


@tool("write_workspace_file")
def write_workspace_file(payload: str) -> str:
    """Write UTF-8 text into a workspace file. Input format: path=<relative_path>\ncontent=<file_content>."""
    try:
        if "\ncontent=" not in payload or not payload.startswith("path="):
            return "Invalid payload. Expected format: path=<relative_path>\\ncontent=<file_content>"

        path_part, content_part = payload.split("\ncontent=", maxsplit=1)
        relative_path = path_part.removeprefix("path=").strip()
        content = content_part

        if not relative_path:
            return "Write error: relative path cannot be empty."

        target = _resolve_workspace_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} characters to {relative_path}"
    except Exception as exc:  # noqa: BLE001
        return f"Write error: {exc}"
