from agent import format_reasoning_trace, run_agent_turn


class DummyAction:
    def __init__(self, tool: str, tool_input: str):
        self.tool = tool
        self.tool_input = tool_input


class DummyExecutor:
    def invoke(self, payload):
        assert payload["input"] == "test goal"
        return {
            "output": "done",
            "intermediate_steps": [
                (DummyAction("calculator", "2+2"), "4"),
                (DummyAction("scratchpad_write", "key=x\\nvalue=4"), "Stored note 'x'."),
            ],
        }


def test_run_agent_turn_uses_executor(monkeypatch):
    monkeypatch.setattr("agent.build_agent_executor", lambda session_id, debug: DummyExecutor())

    result = run_agent_turn("test goal", session_id="abc", debug=True)

    assert result["output"] == "done"
    assert len(result["intermediate_steps"]) == 2


def test_format_reasoning_trace_from_intermediate_steps():
    steps = [(DummyAction("calculator", "10/2"), "5")]

    trace = format_reasoning_trace(steps)

    assert "TOOL: calculator" in trace[0]
    assert "OBSERVATION: 5" in trace[1]
