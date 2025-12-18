"""Tests for exception classes."""


from nexus_client.exceptions import (
    ConflictError,
    InvalidPathError,
    NexusError,
    NexusFileNotFoundError,
    NexusPermissionError,
    RemoteConnectionError,
    RemoteFilesystemError,
    RemoteTimeoutError,
    ValidationError,
)


def test_nexus_error_basic():
    """Test basic NexusError."""
    error = NexusError("Something went wrong")
    assert str(error) == "Something went wrong"
    assert error.path is None


def test_nexus_error_with_path():
    """Test NexusError with path."""
    error = NexusError("File error", path="/test.txt")
    assert str(error) == "File error: /test.txt"
    assert error.path == "/test.txt"


def test_nexus_file_not_found_error():
    """Test NexusFileNotFoundError."""
    error = NexusFileNotFoundError("/missing.txt")
    assert str(error) == "File not found: /missing.txt"
    assert error.path == "/missing.txt"
    assert isinstance(error, FileNotFoundError)


def test_nexus_permission_error():
    """Test NexusPermissionError."""
    error = NexusPermissionError("/protected.txt", "Access denied")
    assert str(error) == "Access denied: /protected.txt"
    assert error.path == "/protected.txt"


def test_invalid_path_error():
    """Test InvalidPathError."""
    error = InvalidPathError("/invalid/path")
    assert str(error) == "Invalid path: /invalid/path"
    assert error.path == "/invalid/path"


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid input", path="/data.json")
    assert str(error) == "Invalid input: /data.json"
    assert error.path == "/data.json"


def test_conflict_error():
    """Test ConflictError."""
    error = ConflictError("/file.txt", "abc123", "def456")
    assert "/file.txt" in str(error)
    assert "abc123" in str(error)
    assert "def456" in str(error)
    assert error.path == "/file.txt"
    assert error.expected_etag == "abc123"
    assert error.current_etag == "def456"


def test_remote_connection_error():
    """Test RemoteConnectionError."""
    error = RemoteConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, RemoteFilesystemError)


def test_remote_timeout_error():
    """Test RemoteTimeoutError."""
    error = RemoteTimeoutError("Request timed out")
    assert str(error) == "Request timed out"
    assert isinstance(error, RemoteFilesystemError)
