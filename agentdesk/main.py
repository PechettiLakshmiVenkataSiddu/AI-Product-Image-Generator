from __future__ import annotations

import typer

from agent import format_reasoning_trace, run_agent_turn
from config import get_settings, setup_logging

app = typer.Typer(help="AgentDesk CLI")


def _print_result(result: dict, debug: bool) -> None:
    typer.echo(f"\nAgentDesk:\n{result.get('output', '')}\n")
    if debug:
        trace = format_reasoning_trace(result.get("intermediate_steps", []))
        if trace:
            typer.echo("Reasoning trace:")
            for line in trace:
                typer.echo(line)


@app.command()
def chat(
    message: str = typer.Option("", "--message", "-m", help="Send one message and exit."),
    session_id: str = typer.Option("cli-default", help="Conversation session ID for memory."),
    debug: bool = typer.Option(False, "--debug", help="Show intermediate tool reasoning trace."),
) -> None:
    """Run AgentDesk in one-shot or interactive mode."""
    settings = get_settings()
    setup_logging(settings)

    if message:
        result = run_agent_turn(message=message, session_id=session_id, debug=debug)
        _print_result(result, debug)
        return

    typer.echo("AgentDesk interactive chat. Type 'exit' to quit.")
    while True:
        user_input = typer.prompt("You")
        if user_input.strip().lower() in {"exit", "quit"}:
            typer.echo("Goodbye.")
            break

        result = run_agent_turn(message=user_input, session_id=session_id, debug=debug)
        _print_result(result, debug)


if __name__ == "__main__":
    app()
