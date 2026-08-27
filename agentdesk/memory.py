from __future__ import annotations

from langchain.memory import ConversationBufferMemory

_SESSION_MEMORIES: dict[str, ConversationBufferMemory] = {}


def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in _SESSION_MEMORIES:
        _SESSION_MEMORIES[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output",
        )
    return _SESSION_MEMORIES[session_id]
