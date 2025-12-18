"""Tests for RemoteNexusFS client."""

from __future__ import annotations

from unittest.mock import Mock, patch

import httpx
import pytest

from nexus_client import RemoteMemory, RemoteNexusFS
from nexus_client.exceptions import (
    ConflictError,
    NexusFileNotFoundError,
    NexusPermissionError,
    RemoteConnectionError,
    RemoteFilesystemError,
    RemoteTimeoutError,
    ValidationError,
)
from nexus_client.protocol import RPCErrorCode, encode_rpc_message


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx Client."""
    client = Mock(spec=httpx.Client)
    client.headers = {}
    return client


@pytest.fixture
def remote_client(mock_httpx_client):
    """Create a RemoteNexusFS instance with mocked httpx client."""
    with patch("nexus_client.client.httpx.Client", return_value=mock_httpx_client):
        client = RemoteNexusFS(
            server_url="http://localhost:8080",
            api_key="test-key",
            timeout=30.0,
            connect_timeout=5.0,
            max_retries=1,  # Reduce retries for faster tests
        )
        client.session = mock_httpx_client
        # Mock auth info fetch to avoid actual HTTP call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "authenticated": True,
            "tenant_id": "test-tenant",
            "subject_type": "user",
            "subject_id": "test-user",
        }
        mock_httpx_client.get.return_value = mock_response
        client._tenant_id = "test-tenant"
        return client


class TestRemoteNexusFSInitialization:
    """Test RemoteNexusFS initialization."""

    def test_initialization_with_api_key(self):
        """Test client initialization with API key."""
        client = RemoteNexusFS("http://localhost:8080", api_key="my-secret", timeout=60)
        assert client.server_url == "http://localhost:8080"
        assert client.api_key == "my-secret"
        assert client.timeout == 60
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer my-secret"
        client.close()

    def test_initialization_without_api_key(self):
        """Test client initialization without API key."""
        client = RemoteNexusFS("http://localhost:8080")
        assert client.api_key is None
        assert "Authorization" not in client.session.headers
        client.close()

    def test_initialization_timeout_settings(self):
        """Test timeout configuration."""
        client = RemoteNexusFS(
            "http://localhost:8080",
            timeout=90,
            connect_timeout=10,
            max_retries=5,
        )
        assert client.timeout == 90
        assert client.connect_timeout == 10
        assert client.max_retries == 5
        client.close()


class TestRemoteNexusFSRPCCalls:
    """Test RPC call functionality."""

    def test_call_rpc_success(self, remote_client, mock_httpx_client):
        """Test successful RPC call."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"exists": True},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        result = remote_client._call_rpc("exists", {"path": "/test.txt"})
        assert result == {"exists": True}

    def test_call_rpc_with_error_response(self, remote_client, mock_httpx_client):
        """Test RPC call with error response."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "error": {
                "code": RPCErrorCode.FILE_NOT_FOUND.value,
                "message": "File not found",
                "data": {"path": "/missing.txt"},
            },
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(NexusFileNotFoundError):
            remote_client._call_rpc("read", {"path": "/missing.txt"})

    def test_call_rpc_connection_error(self, remote_client, mock_httpx_client):
        """Test RPC call with connection error."""
        # Set side_effect to always raise ConnectError
        # The retry decorator will retry on ConnectError (up to 3 times by default)
        # then convert to RemoteConnectionError and raise
        mock_httpx_client.post.side_effect = httpx.ConnectError("Connection failed")

        # Helper function to catch exceptions from retry-decorated functions
        # pytest.raises doesn't work well with tenacity retry decorator
        def call_with_catch(func, *args, **kwargs):
            try:
                return func(*args, **kwargs), None
            except Exception as e:
                return None, e

        result, exception = call_with_catch(remote_client._call_rpc, "read", {"path": "/test.txt"})
        # Verify exception was raised and has correct properties
        assert exception is not None, "Expected RemoteConnectionError to be raised"
        assert isinstance(exception, RemoteConnectionError)
        assert "Failed to connect" in str(exception) or "Connection failed" in str(exception)
        assert exception.method == "read"

    def test_call_rpc_timeout_error(self, remote_client, mock_httpx_client):
        """Test RPC call with timeout error."""
        # Set side_effect to always raise TimeoutException
        mock_httpx_client.post.side_effect = httpx.TimeoutException("Request timed out")

        # Helper function to catch exceptions from retry-decorated functions
        def call_with_catch(func, *args, **kwargs):
            try:
                return func(*args, **kwargs), None
            except Exception as e:
                return None, e

        result, exception = call_with_catch(remote_client._call_rpc, "read", {"path": "/test.txt"})
        # Verify exception was raised and has correct properties
        assert exception is not None, "Expected RemoteTimeoutError to be raised"
        assert isinstance(exception, RemoteTimeoutError)
        assert "timed out" in str(exception).lower() or "Request timed out" in str(exception)
        assert exception.method == "read"

    def test_call_rpc_http_error(self, remote_client, mock_httpx_client):
        """Test RPC call with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        # Reset side_effect if it was set in previous tests
        mock_httpx_client.post.side_effect = None
        mock_httpx_client.post.return_value = mock_response

        # HTTP errors don't retry (not in retry list), so should raise immediately
        # Helper function to catch exceptions from retry-decorated functions
        def call_with_catch(func, *args, **kwargs):
            try:
                return func(*args, **kwargs), None
            except Exception as e:
                return None, e

        result, exception = call_with_catch(remote_client._call_rpc, "read", {"path": "/test.txt"})
        # Verify exception was raised and has correct properties
        assert exception is not None, "Expected RemoteFilesystemError to be raised"
        assert isinstance(exception, RemoteFilesystemError)
        assert exception.status_code == 500
        assert "Internal Server Error" in str(exception)
        assert exception.method == "read"


class TestRemoteNexusFSFileOperations:
    """Test file operations."""

    def test_read_file(self, remote_client, mock_httpx_client):
        """Test reading a file."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"content": "SGVsbG8gV29ybGQ="},  # base64 "Hello World"
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        content = remote_client.read("/test.txt")
        assert content == b"Hello World"

    def test_write_file(self, remote_client, mock_httpx_client):
        """Test writing a file."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {
                "etag": "abc123",
                "version": 1,
                "modified_at": "2024-01-01T00:00:00",
                "size": 11,
            },
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        result = remote_client.write("/test.txt", b"Hello World")
        assert result["etag"] == "abc123"
        assert result["version"] == 1

    def test_delete_file(self, remote_client, mock_httpx_client):
        """Test deleting a file."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {"jsonrpc": "2.0", "id": "123", "result": None}
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        # Should not raise
        remote_client.delete("/test.txt")

    def test_exists_file(self, remote_client, mock_httpx_client):
        """Test checking if file exists."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {"jsonrpc": "2.0", "id": "123", "result": {"exists": True}}
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        assert remote_client.exists("/test.txt") is True

    def test_list_files(self, remote_client, mock_httpx_client):
        """Test listing files."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"files": ["/file1.txt", "/file2.txt"]},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        files = remote_client.list("/")
        assert files == ["/file1.txt", "/file2.txt"]

    def test_glob_files(self, remote_client, mock_httpx_client):
        """Test glob pattern search."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"matches": ["/file1.py", "/file2.py"]},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        matches = remote_client.glob("*.py", "/")
        assert matches == ["/file1.py", "/file2.py"]

    def test_grep_files(self, remote_client, mock_httpx_client):
        """Test grep search."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {
                "results": [
                    {"file": "/test.py", "line": 1, "content": "def test():", "match": "def"}
                ]
            },
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        results = remote_client.grep("def", "/", file_pattern="*.py")
        assert len(results) == 1
        assert results[0]["file"] == "/test.py"


class TestRemoteMemory:
    """Test RemoteMemory API."""

    def test_memory_store(self, remote_client, mock_httpx_client):
        """Test storing a memory."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"memory_id": "mem-123"},
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        memory = RemoteMemory(remote_client)
        memory_id = memory.store("User prefers dark mode")
        assert memory_id == "mem-123"

    def test_memory_query(self, remote_client, mock_httpx_client):
        """Test querying memories."""
        mock_response = Mock()
        mock_response.status_code = 200
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {
                "memories": [
                    {"memory_id": "mem-1", "content": "Memory 1", "importance": 0.8}
                ]
            },
        }
        mock_response.content = encode_rpc_message(response_data)
        mock_httpx_client.post.return_value = mock_response

        memory = RemoteMemory(remote_client)
        memories = memory.query(limit=10)
        assert len(memories) == 1
        assert memories[0]["content"] == "Memory 1"

    def test_memory_property(self, remote_client):
        """Test memory property lazy initialization."""
        assert remote_client._memory_api is None
        memory = remote_client.memory
        assert isinstance(memory, RemoteMemory)
        assert remote_client._memory_api is not None
        # Second access should return same instance
        assert remote_client.memory is memory


class TestErrorHandling:
    """Test error handling."""

    def test_handle_rpc_error_file_not_found(self, remote_client):
        """Test handling file not found error."""
        error = {
            "code": RPCErrorCode.FILE_NOT_FOUND.value,
            "message": "File not found",
            "data": {"path": "/missing.txt"},
        }

        with pytest.raises(NexusFileNotFoundError):
            remote_client._handle_rpc_error(error)

    def test_handle_rpc_error_permission(self, remote_client):
        """Test handling permission error."""
        error = {
            "code": RPCErrorCode.PERMISSION_ERROR.value,
            "message": "Permission denied",
        }

        with pytest.raises(NexusPermissionError):
            remote_client._handle_rpc_error(error)

    def test_handle_rpc_error_validation(self, remote_client):
        """Test handling validation error."""
        error = {
            "code": RPCErrorCode.VALIDATION_ERROR.value,
            "message": "Invalid input",
        }

        with pytest.raises(ValidationError):
            remote_client._handle_rpc_error(error)

    def test_handle_rpc_error_conflict(self, remote_client):
        """Test handling conflict error."""
        error = {
            "code": RPCErrorCode.CONFLICT.value,
            "message": "Conflict detected",
            "data": {
                "path": "/file.txt",
                "expected_etag": "abc123",
                "current_etag": "def456",
            },
        }

        with pytest.raises(ConflictError) as exc_info:
            remote_client._handle_rpc_error(error)
        assert exc_info.value.expected_etag == "abc123"
        assert exc_info.value.current_etag == "def456"
