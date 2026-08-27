from __future__ import annotations

import ast
import operator

from langchain.tools import tool


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return float(_ALLOWED_BINARY_OPERATORS[type(node.op)](left, right))

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPERATORS:
        operand = _safe_eval(node.operand)
        return float(_ALLOWED_UNARY_OPERATORS[type(node.op)](operand))

    raise ValueError("Unsupported expression. Use only numbers and arithmetic operators.")


@tool("calculator")
def calculator(expression: str) -> str:
    """Evaluate arithmetic expressions safely. Supports +, -, *, /, **, %, //, and parentheses."""
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _safe_eval(parsed)
    except Exception as exc:  # noqa: BLE001
        return f"Calculation error: {exc}"

    if result.is_integer():
        return str(int(result))
    return str(result)
