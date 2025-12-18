"""Tests for LangGraph tools integration."""

from unittest.mock import Mock, patch

import pytest

# Skip tests if LangGraph dependencies not available
try:
    from langchain_core.runnables import RunnableConfig
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    pytestmark = pytest.mark.skip("LangGraph dependencies not installed")

if HAS_LANGGRAPH:
    from nexus_client import RemoteNexusFS
    from nexus_client.langgraph import get_nexus_tools, list_skills
    from nexus_client.langgraph.client import _get_nexus_client


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph dependencies not installed")
class TestLangGraphTools:
    """Test LangGraph tools."""

    def test_get_nexus_tools(self):
        """Test that get_nexus_tools returns list of tools."""
        tools = get_nexus_tools()
        assert len(tools) == 7

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "grep_files",
            "glob_files",
            "read_file",
            "write_file",
            "python",
            "bash",
            "query_memories",
        ]
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    def test_get_nexus_client_from_config(self):
        """Test _get_nexus_client helper."""
        config = RunnableConfig(
            metadata={
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        )

        client = _get_nexus_client(config)
        assert isinstance(client, RemoteNexusFS)
        assert client.api_key == "sk-test-key"
        assert client.server_url == "http://localhost:8080"
        client.close()

    def test_get_nexus_client_missing_auth(self):
        """Test _get_nexus_client with missing auth."""
        config = RunnableConfig(metadata={})

        with pytest.raises(ValueError, match="Missing x_auth"):
            _get_nexus_client(config)

    def test_get_nexus_client_from_state(self):
        """Test _get_nexus_client with state context."""
        config = RunnableConfig(metadata={})
        state = {
            "context": {
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        }

        client = _get_nexus_client(config, state)
        assert isinstance(client, RemoteNexusFS)
        assert client.api_key == "sk-test-key"
        client.close()


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph dependencies not installed")
class TestListSkills:
    """Test list_skills function."""

    def test_list_skills(self):
        """Test list_skills function."""
        config = RunnableConfig(
            metadata={
                "x_auth": "Bearer sk-test-key",
                "nexus_server_url": "http://localhost:8080",
            }
        )

        # Mock the client to avoid actual RPC calls
        # Need to patch both _get_nexus_client and the client's skills_list method
        with patch("nexus_client.langgraph.tools._get_nexus_client") as mock_get_client:
            mock_client = Mock(spec=RemoteNexusFS)
            mock_client.skills_list.return_value = {
                "skills": [{"name": "test-skill", "description": "Test"}],
                "count": 1,
            }
            mock_get_client.return_value = mock_client

            result = list_skills(config)
            assert "skills" in result
            assert "count" in result
            assert result["count"] == 1
            # Verify the client was created and skills_list was called
            mock_get_client.assert_called_once_with(config, None)
            mock_client.skills_list.assert_called_once_with(tier=None, include_metadata=True)
