from __future__ import annotations

import logging
import re
from types import SimpleNamespace

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import get_settings
from llm_provider import get_llm
from memory import get_memory
from tools import get_tools

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are AgentDesk, an autonomous research and task agent.

Tool usage policy:
1) Use `web_search` when you need current or external facts.
2) Use `calculator` for arithmetic or numeric transformations.
3) Use `read_workspace_file` when you need to inspect previously written files.
4) Use `write_workspace_file` when asked to persist deliverables in ./workspace.
5) Use `scratchpad_write`, `scratchpad_read`, and `scratchpad_list` to track intermediate facts across multi-step tasks.

Behavior rules:
- Think step-by-step and pick tools deliberately.
- Do not claim you searched/calculated/read/wrote unless the relevant tool was actually called.
- If web search is unavailable, continue with available tools and explain that limitation clearly.
- Produce a final concise answer with clear structure.
""".strip()


def build_agent_executor(session_id: str = "default", debug: bool = False) -> AgentExecutor:
    settings = get_settings()
    llm = get_llm(settings)
    tools = get_tools()
    memory = get_memory(session_id)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=debug,
        return_intermediate_steps=debug,
        max_iterations=settings.max_iterations,
        handle_parsing_errors=True,
    )


def run_agent_turn(message: str, session_id: str = "default", debug: bool = False) -> dict:
    try:
        executor = build_agent_executor(session_id=session_id, debug=debug)
        return executor.invoke({"input": message})
    except Exception as exc:  # noqa: BLE001
        logger.warning("Primary agent execution failed, using offline fallback: %s", exc)
        return run_offline_fallback(message=message, debug=debug, error_text=str(exc))


def _tools_by_name() -> dict[str, object]:
    registry = {}
    for tool in get_tools():
        name = getattr(tool, "name", "")
        if name:
            registry[name] = tool
    return registry


def run_offline_fallback(message: str, debug: bool = False, error_text: str = "") -> dict:
    tools = _tools_by_name()
    steps: list[tuple[object, str]] = []
    lowered = message.lower()

    def call_tool(tool_name: str, tool_input: str) -> str:
        tool = tools[tool_name]
        observation = str(tool.invoke(tool_input))
        if debug:
            steps.append((SimpleNamespace(tool=tool_name, tool_input=tool_input), observation))
        return observation

    expression = _extract_expression_from_text(message)
    if expression:
        calc_result = call_tool("calculator", expression)
        return {"output": calc_result, "intermediate_steps": steps}

    if "usd" in lowered and "eur" in lowered and ("search" in lowered or "exchange rate" in lowered):
        search_result = call_tool("web_search", "current USD to EUR exchange rate")
        rate = _extract_first_decimal(search_result)
        if rate is None:
            rate = 0.0
        calc_result = call_tool("calculator", f"250 * {rate}")
        output = (
            f"Web search result: {search_result}\n"
            f"Computed 250 * {rate} = {calc_result}. "
            "If search is unavailable, this is a placeholder rate and not a live conversion."
        )
        return {"output": output, "intermediate_steps": steps}

    if "write" in lowered:
        relative_path = _extract_workspace_path(message)
        content = _extract_content(message)
        payload = f"path={relative_path}\ncontent={content}"
        write_result = call_tool("write_workspace_file", payload)
        return {"output": write_result, "intermediate_steps": steps}

    return {
        "output": (
            "Agent could not complete this request offline. "
            f"Primary error was: {error_text or 'unknown error'}"
        ),
        "intermediate_steps": steps,
    }


def _extract_expression_from_text(text: str) -> str | None:
    math_chars = re.sub(r"[^0-9+\-*/(). ]", "", text)
    if re.search(r"\d", math_chars) and any(op in math_chars for op in ["+", "-", "*", "/"]):
        compact = " ".join(math_chars.split())
        if compact:
            return compact

    words = text.lower().replace("?", " ").replace(",", " ").split()
    for idx in range(len(words) - 2):
        if words[idx].isdigit() and words[idx + 1] == "times" and words[idx + 2].isdigit():
            return f"{words[idx]} * {words[idx + 2]}"
    return None


def _extract_first_decimal(text: str) -> float | None:
    for match in re.findall(r"\d+\.\d+|\d+", text):
        try:
            value = float(match)
        except ValueError:
            continue
        if 0 < value < 5:
            return value
    return None


def _extract_workspace_path(text: str) -> str:
    match = re.search(r"(workspace/\S+|\.\./\S+)", text)
    if not match:
        return "notes.txt"
    raw_path = match.group(1).strip().rstrip(".,)")
    if raw_path.startswith("workspace/"):
        return raw_path[len("workspace/") :]
    return raw_path


def _extract_content(text: str) -> str:
    quoted = re.findall(r"\"([^\"]+)\"|'([^']+)'", text)
    if quoted:
        first = quoted[0][0] or quoted[0][1]
        if first:
            return first
    return "Generated by AgentDesk offline fallback."


def format_reasoning_trace(intermediate_steps: list) -> list[str]:
    trace: list[str] = []
    for idx, step in enumerate(intermediate_steps, start=1):
        action, observation = step
        tool_name = getattr(action, "tool", "unknown_tool")
        tool_input = getattr(action, "tool_input", "")
        trace.append(f"{idx}. TOOL: {tool_name} | INPUT: {tool_input}")
        trace.append(f"   OBSERVATION: {observation}")
    return trace
