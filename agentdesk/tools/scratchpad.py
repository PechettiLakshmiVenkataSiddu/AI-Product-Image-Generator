from __future__ import annotations

from langchain.tools import tool

_NOTES: dict[str, str] = {}


@tool("scratchpad_write")
def scratchpad_write(payload: str) -> str:
    """Save a short note. Input format: key=<note_key>\nvalue=<note_value>."""
    if "\nvalue=" not in payload or not payload.startswith("key="):
        return "Invalid payload. Expected format: key=<note_key>\\nvalue=<note_value>"

    key_part, value_part = payload.split("\nvalue=", maxsplit=1)
    key = key_part.removeprefix("key=").strip()
    value = value_part.strip()

    if not key:
        return "Scratchpad error: key cannot be empty."

    _NOTES[key] = value
    return f"Stored note '{key}'."


@tool("scratchpad_read")
def scratchpad_read(key: str) -> str:
    """Read a saved note by key."""
    if key not in _NOTES:
        return f"No note found for key: {key}"
    return _NOTES[key]


@tool("scratchpad_list")
def scratchpad_list(_: str = "") -> str:
    """List all scratchpad note keys."""
    if not _NOTES:
        return "No scratchpad notes saved."
    return ", ".join(sorted(_NOTES.keys()))
