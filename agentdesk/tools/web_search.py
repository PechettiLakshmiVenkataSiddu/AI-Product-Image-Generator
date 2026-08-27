from __future__ import annotations

import logging
import os

from langchain.tools import tool

from config import get_settings

logger = logging.getLogger(__name__)


def get_web_search_tool():
    settings = get_settings()

    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set; web search tool is running in fallback mode.")

        @tool("web_search")
        def search_unavailable(query: str) -> str:
            """Fallback web search tool used when Tavily is unavailable."""
            return f"search unavailable: Tavily API key missing. Query was: {query}"

        return search_unavailable

    try:
        from langchain_community.tools.tavily_search import TavilySearchResults

        os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
        return TavilySearchResults(max_results=5)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to initialize Tavily search (%s). Using fallback search tool.", exc)

        @tool("web_search")
        def search_unavailable(query: str) -> str:
            """Fallback web search tool used when Tavily initialization fails."""
            return f"search unavailable: Tavily setup failed. Query was: {query}"

        return search_unavailable
