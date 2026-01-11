"""Tests for LangGraph tools integration."""

from unittest.mock import patch

import pytest

# Skip tests if LangGraph dependencies not available
try:
    from langchain_core.runnables import RunnableConfig
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    pytestmark = pytest.mark.skip("LangGraph dependencies not installed")

if HAS_LANGGRAPH:
    from nexus_client import AsyncRemoteNexusFS
    from nexus_client.langgraph import get_nexus_tools, skills_discover
    from nexus_client.langgraph.client import _get_nexus_client


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph dependencies not installed")
class TestLangGraphTools:
    """Test LangGraph tools."""

    def test_get_nexus_tools(self):
        """Test that get_nexus_tools returns list of tools."""
        tools = get_nexus_tools()
        assert len(tools) == 6

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "grep_files",
            "glob_files",
            "read_file",
            "write_file",
            "python",
            "bash",
        ]
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    @pytest.mark.asyncio
    async def test_get_nexus_client_from_config(self):
        """Test _get_nexus_client helper."""
        config = RunnableConfig(
            metadata={
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        )

        client = await _get_nexus_client(config)
        assert isinstance(client, AsyncRemoteNexusFS)
        assert client.api_key == "sk-test-key"
        assert client.server_url == "http://localhost:8080"
        await client.close()

    @pytest.mark.asyncio
    async def test_get_nexus_client_missing_auth(self):
        """Test _get_nexus_client with missing auth."""
        config = RunnableConfig(metadata={})

        with pytest.raises(ValueError, match="Missing x_auth"):
            await _get_nexus_client(config)

    @pytest.mark.asyncio
    async def test_get_nexus_client_from_state(self):
        """Test _get_nexus_client with state context."""
        config = RunnableConfig(metadata={})
        state = {
            "context": {
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        }

        client = await _get_nexus_client(config, state)
        assert isinstance(client, AsyncRemoteNexusFS)
        assert client.api_key == "sk-test-key"
        await client.close()


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph dependencies not installed")
class TestSkillsDiscover:
    """Test skills_discover function."""

    @pytest.mark.asyncio
    async def test_skills_discover(self):
        """Test skills_discover function."""
        from unittest.mock import AsyncMock

        config = RunnableConfig(
            metadata={
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        )

        # Mock the async client to avoid actual RPC calls
        # Need to patch _get_nexus_client and the client's skills_discover method
        with patch("nexus_client.langgraph.prompt._get_nexus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.skills_discover = AsyncMock(return_value={
                "skills": [{"name": "test-skill", "description": "Test"}],
                "count": 1,
            })
            mock_get_client.return_value = mock_client

            result = await skills_discover(config)
            assert "skills" in result
            assert "count" in result
            assert result["count"] == 1
            # Verify the client was created and skills_discover was called
            mock_get_client.assert_called_once()
            mock_client.skills_discover.assert_called_once_with(filter="subscribed")

