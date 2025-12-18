"""LangGraph integration for Nexus client.

This module provides LangGraph tool adaptors for using Nexus with LangGraph agents.

Requires optional dependencies:
    pip install nexus-fs-python[langgraph]

Example:
    >>> from nexus_client.langgraph import get_nexus_tools
    >>> from langgraph.prebuilt import create_react_agent
    >>>
    >>> tools = get_nexus_tools()
    >>> agent = create_react_agent(model=llm, tools=tools)
    >>>
    >>> result = agent.invoke(
    ...     {"messages": [{"role": "user", "content": "Find Python files"}]},
    ...     config={"metadata": {"x_auth": "Bearer sk-xxx", "nexus_server_url": "http://localhost:8080"}}
    ... )
"""

try:
    # Re-export RemoteNexusFS for backward compatibility
    from nexus_client import RemoteNexusFS
    from nexus_client.langgraph.client import _get_nexus_client
    from nexus_client.langgraph.tools import get_nexus_tools, list_skills

    __all__ = [
        "get_nexus_tools",
        "list_skills",
        "_get_nexus_client",
        "RemoteNexusFS",
    ]
except ImportError as e:
    # LangGraph dependencies not installed
    _missing_deps = str(e)
    raise ImportError(
        f"LangGraph integration requires optional dependencies. "
        f"Install with: pip install nexus-fs-python[langgraph]\n"
        f"Missing: {_missing_deps}"
    ) from e
