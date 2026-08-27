from __future__ import annotations

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import get_settings
from llm_provider import get_llm
from memory import get_memory
from tools import get_tools

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
    executor = build_agent_executor(session_id=session_id, debug=debug)
    return executor.invoke({"input": message})


def format_reasoning_trace(intermediate_steps: list) -> list[str]:
    trace: list[str] = []
    for idx, step in enumerate(intermediate_steps, start=1):
        action, observation = step
        tool_name = getattr(action, "tool", "unknown_tool")
        tool_input = getattr(action, "tool_input", "")
        trace.append(f"{idx}. TOOL: {tool_name} | INPUT: {tool_input}")
        trace.append(f"   OBSERVATION: {observation}")
    return trace
