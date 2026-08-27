from tools.calculator import calculator
from tools.file_ops import read_workspace_file, write_workspace_file
from tools.scratchpad import scratchpad_list, scratchpad_read, scratchpad_write
from tools.web_search import get_web_search_tool


def get_tools():
    return [
        get_web_search_tool(),
        calculator,
        read_workspace_file,
        write_workspace_file,
        scratchpad_write,
        scratchpad_read,
        scratchpad_list,
    ]
