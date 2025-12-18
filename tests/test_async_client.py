"""Tests for AsyncRemoteNexusFS client."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from nexus_client import AsyncRemoteMemory, AsyncRemoteNexusFS
from nexus_client.exceptions import RemoteConnectionError
from nexus_client.protocol import encode_rpc_message


@pytest.fixture
def mock_async_httpx_client():
    """Create a mock httpx AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.headers = {}
    return client


@pytest.fixture
async def async_remote_client(mock_async_httpx_client):
    """Create an AsyncRemoteNexusFS instance with mocked httpx client."""
    with patch("nexus_client.async_client.httpx.AsyncClient", return_value=mock_async_httpx_client):
        client = AsyncRemoteNexusFS(
            server_url="http://localhost:8080",
            api_key="test-key",
            timeout=30.0,
            connect_timeout=5.0,
        )
        client._client = mock_async_httpx_client
        client._initialized = True
        client._tenant_id = "test-tenant"
        # Mock the auth info fetch
        mock_async_httpx_client.get = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "authenticated": True,
            "tenant_id": "test-tenant",
            "subject_type": "user",
            "subject_id": "test-user",
        })
        mock_async_httpx_client.get.return_value = mock_response
        return client


@pytest.mark.asyncio
class TestAsyncRemoteNexusFS:
    """Test AsyncRemoteNexusFS functionality."""

    async def test_initialization(self):
        """Test async client initialization."""
        client = AsyncRemoteNexusFS("http://localhost:8080", api_key="test-key")
        assert client.server_url == "http://localhost:8080"
        assert client.api_key == "test-key"
        assert "Authorization" in client._client.headers
        await client.close()

    async def test_context_manager(self, async_remote_client):
        """Test async context manager."""
        async with async_remote_client as client:
            assert client._initialized is True
        # Client should be closed after context exit
        assert async_remote_client._client.aclose.called

    async def test_read_file(self, async_remote_client, mock_async_httpx_client):
        """Test async file read."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"content": "SGVsbG8gV29ybGQ="},  # base64 "Hello World"
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_async_httpx_client.post.return_value = mock_response

        content = await async_remote_client.read("/test.txt")
        assert content == b"Hello World"

    async def test_write_file(self, async_remote_client, mock_async_httpx_client):
        """Test async file write."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"etag": "abc123", "version": 1, "size": 11},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_async_httpx_client.post.return_value = mock_response

        result = await async_remote_client.write("/test.txt", b"Hello World")
        assert result["etag"] == "abc123"

    async def test_connection_error(self, async_remote_client, mock_async_httpx_client):
        """Test async connection error handling."""
        mock_async_httpx_client.post.side_effect = httpx.ConnectError("Connection failed")

        with pytest.raises(RemoteConnectionError):
            await async_remote_client.read("/test.txt")


@pytest.mark.asyncio
class TestAsyncRemoteMemory:
    """Test AsyncRemoteMemory functionality."""

    async def test_memory_store(self, async_remote_client, mock_async_httpx_client):
        """Test async memory store."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"memory_id": "mem-123"},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_async_httpx_client.post.return_value = mock_response

        memory = AsyncRemoteMemory(async_remote_client)
        memory_id = await memory.store("Test memory")
        assert memory_id == "mem-123"

    async def test_memory_query(self, async_remote_client, mock_async_httpx_client):
        """Test async memory query."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"memories": [{"memory_id": "mem-1", "content": "Memory 1"}]},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_async_httpx_client.post.return_value = mock_response

        memory = AsyncRemoteMemory(async_remote_client)
        memories = await memory.query(limit=10)
        assert len(memories) == 1
