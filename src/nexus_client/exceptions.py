"""Custom exceptions for Nexus filesystem operations."""

from typing import Any


class NexusError(Exception):
    """Base exception for all Nexus errors."""

    def __init__(self, message: str, path: str | None = None):
        self.message = message
        self.path = path
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with optional path."""
        if self.path:
            return f"{self.message}: {self.path}"
        return self.message


class NexusFileNotFoundError(NexusError, FileNotFoundError):
    """Raised when a file or directory does not exist."""

    def __init__(self, path: str, message: str | None = None):
        msg = message or "File not found"
        super().__init__(msg, path)


class NexusPermissionError(NexusError):
    """Raised when access to a file or directory is denied."""

    def __init__(self, path: str, message: str | None = None):
        msg = message or "Permission denied"
        super().__init__(msg, path)


class PermissionDeniedError(NexusError):
    """Raised when ReBAC permission check fails.

    This is used by ReBAC-enabled operations (skills, memory, etc.) when
    a subject lacks the required permission on an object.
    """

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message, path)


class BackendError(NexusError):
    """Raised when a backend operation fails."""

    def __init__(self, message: str, backend: str | None = None, path: str | None = None):
        self.backend = backend
        if backend:
            message = f"[{backend}] {message}"
        super().__init__(message, path)


class InvalidPathError(NexusError):
    """Raised when a path is invalid or contains illegal characters."""

    def __init__(self, path: str, message: str | None = None):
        msg = message or "Invalid path"
        super().__init__(msg, path)


class MetadataError(NexusError):
    """Raised when metadata operations fail."""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message, path)


class ValidationError(NexusError):
    """Raised when validation fails.

    This is a domain error that should be caught and converted to
    appropriate HTTP status codes (400 Bad Request) in API layers.
    """

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message, path)


class ParserError(NexusError):
    """Raised when document parsing fails."""

    def __init__(self, message: str, path: str | None = None, parser: str | None = None):
        self.parser = parser
        if parser:
            message = f"[{parser}] {message}"
        super().__init__(message, path)


class ConflictError(NexusError):
    """Raised when optimistic concurrency check fails.

    This occurs when a write operation specifies an if_match etag/version
    that doesn't match the current file version, indicating another agent
    has modified the file concurrently.
    """

    def __init__(self, path: str, expected_etag: str, current_etag: str):
        """Initialize conflict error.

        Args:
            path: Virtual file path that had the conflict
            expected_etag: The etag value that was expected (from if_match)
            current_etag: The actual current etag value in the database
        """
        self.expected_etag = expected_etag
        self.current_etag = current_etag
        message = (
            f"Conflict detected - file was modified by another agent. "
            f"Expected etag '{expected_etag[:16]}...', but current etag is '{current_etag[:16]}...'"
        )
        super().__init__(message, path)


class AuditLogError(NexusError):
    """Raised when audit logging fails and audit_strict_mode is enabled."""

    def __init__(
        self, message: str, path: str | None = None, original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, path)


class AuthenticationError(NexusError):
    """Raised when authentication fails."""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message, path)


# Remote client specific exceptions
class RemoteFilesystemError(NexusError):
    """Enhanced remote filesystem error with detailed information.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (if applicable)
        details: Additional error details
        method: RPC method that failed
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        method: str | None = None,
        path: str | None = None,
    ):
        """Initialize remote filesystem error.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
            method: RPC method that failed
            path: Optional file path (for compatibility with NexusError)
        """
        self.status_code = status_code
        self.details = details or {}
        self.method = method

        # Build detailed error message
        error_parts = [message]
        if method:
            error_parts.append(f"(method: {method})")
        if status_code:
            error_parts.append(f"[HTTP {status_code}]")

        super().__init__(" ".join(error_parts), path)


class RemoteConnectionError(RemoteFilesystemError):
    """Error connecting to remote Nexus server."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        method: str | None = None,
        path: str | None = None,
    ):
        """Initialize connection error."""
        super().__init__(message, status_code=None, details=details, method=method, path=path)


class RemoteTimeoutError(RemoteFilesystemError):
    """Timeout while communicating with remote server."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        method: str | None = None,
        path: str | None = None,
    ):
        """Initialize timeout error."""
        super().__init__(message, status_code=None, details=details, method=method, path=path)


# Alias for convenience
NotFoundError = NexusFileNotFoundError
