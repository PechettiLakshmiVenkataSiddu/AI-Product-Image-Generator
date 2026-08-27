from pathlib import Path

from config import get_settings
from tools.calculator import calculator
from tools.file_ops import read_workspace_file, write_workspace_file
from tools.web_search import get_web_search_tool


def test_calculator_handles_arithmetic_and_blocks_invalid_code():
    assert calculator.invoke("(2 + 3) * 4") == "20"
    error_text = calculator.invoke("__import__('os').system('echo unsafe')")
    assert "Calculation error" in error_text


def test_workspace_file_tools_are_sandboxed(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path))
    get_settings.cache_clear()

    write_result = write_workspace_file.invoke("path=notes/demo.txt\ncontent=hello workspace")
    read_result = read_workspace_file.invoke("notes/demo.txt")
    blocked_result = read_workspace_file.invoke("../outside.txt")

    assert "Wrote" in write_result
    assert read_result == "hello workspace"
    assert "Access denied" in blocked_result

    expected_path = Path(tmp_path) / "notes" / "demo.txt"
    assert expected_path.exists()


def test_web_search_fallback_without_tavily_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    get_settings.cache_clear()

    web_search_tool = get_web_search_tool()
    result = web_search_tool.invoke("latest AI agent benchmarks")

    assert "search unavailable" in result
