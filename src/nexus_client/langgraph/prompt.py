"""Prompt generation utilities for LangGraph agents.

This module provides functions for generating system prompts with skills context.
These are NOT tools for agents to call - they are utilities used during prompt generation.
"""

from typing import Annotated, Any, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import InjectedState

from nexus_client.langgraph.client import _get_nexus_client

__all__ = [
    "list_skills",
    "get_prompt_context",
]


def get_prompt_context(
    config: RunnableConfig,
    state: Annotated[Any, InjectedState] = None,
    max_skills: int = 50,
) -> dict[str, Any]:
    """Get skill metadata formatted for system prompt injection.

    This is a synchronous wrapper that calls the Nexus RPC method skills_get_prompt_context
    which returns skills formatted as XML for system prompts.

    Args:
        config: Runtime configuration containing auth metadata
        state: Optional agent state
        max_skills: Maximum number of skills to include (default: 50)

    Returns:
        Dictionary with:
            - "xml": Formatted XML string of skills
            - "skills": List of skill dictionaries
            - "count": Total number of skills
    """
    from nexus_client.langgraph.client import _get_nexus_client_sync

    try:
        nx = _get_nexus_client_sync(config, state)
        return nx.skills_get_prompt_context(max_skills=max_skills)
    except ValueError:
        # If no auth is available (e.g., during schema generation), return empty result
        return {"xml": "", "skills": [], "count": 0}


async def skills_discover(
    config: RunnableConfig,
    state: Annotated[Any, InjectedState] = None,
    filter: Literal["subscribed", "owned", "public", "all"] = "subscribed",
) -> dict[str, Any]:
    """List available skills from Nexus for prompt generation.

    This is a standalone function (not a LangGraph tool) that returns skill data
    for programmatic use in system prompt generation.

    Args:
        config: Runtime configuration (provided by framework) containing auth metadata
        state: Agent state (injected by LangGraph, not used directly)
        filter: Filter type - "subscribed" (default) or "available"

    Available Filters:
        - "subscribed": Show only subscribed skills (default)
        - "available": Show all available skills

    Returns:
        Dictionary with:
            - "skills": List of skill dictionaries with name, description, version, tier, etc.
            - "count": Total number of skills

    Examples:
        >>> from langchain_core.runnables import RunnableConfig
        >>> from nexus_client.langgraph.prompt import list_skills
        >>>
        >>> config = RunnableConfig(metadata={
        ...     "x_auth": "Bearer sk-your-api-key",
        ...     "nexus_server_url": "http://localhost:8080"
        ... })
        >>>
        >>> # Get subscribed skills (default)
        >>> result = await list_skills(config)
        >>> print(f"Found {result['count']} skills")
        >>>
        >>> # Get all available skills
        >>> result = await list_skills(config, filter="available")
        >>> print(f"Found {result['count']} available skills")
    """
    try:
        nx = await _get_nexus_client(config, state)
        return await nx.skills_discover(filter=filter)
    except ValueError:
        # If no auth is available (e.g., during schema generation), return empty result
        return {"skills": [], "count": 0}
