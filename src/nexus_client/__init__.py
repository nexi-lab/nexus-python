"""Nexus Python Client SDK.

A lightweight Python 3.11+ client SDK for Nexus filesystem, designed for LangGraph deployments.

Example:
    >>> from nexus_client import RemoteNexusFS
    >>> nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")
    >>> content = nx.read("/workspace/file.txt")
    >>> nx.write("/workspace/output.txt", b"Hello, World!")
"""

__version__ = "0.1.0"

# Protocol exports
from nexus_client.async_client import AsyncRemoteMemory, AsyncRemoteNexusFS

# Client exports
from nexus_client.client import RemoteMemory, RemoteNexusFS

# Exception exports
from nexus_client.exceptions import (
    AuditLogError,
    AuthenticationError,
    BackendError,
    ConflictError,
    InvalidPathError,
    MetadataError,
    NexusError,
    NexusFileNotFoundError,
    NexusPermissionError,
    NotFoundError,
    ParserError,
    PermissionDeniedError,
    RemoteConnectionError,
    RemoteFilesystemError,
    RemoteTimeoutError,
    ValidationError,
)
from nexus_client.protocol import (
    RPCErrorCode,
    RPCRequest,
    RPCResponse,
    decode_rpc_message,
    encode_rpc_message,
)

# LangGraph exports (optional - requires langgraph optional dependencies)
try:
    from nexus_client.langgraph import get_nexus_tools, list_skills
    _HAS_LANGGRAPH = True
except ImportError:
    # LangGraph dependencies not installed
    _HAS_LANGGRAPH = False
    # Don't export these if dependencies aren't available
    def _langgraph_not_available():
        raise ImportError(
            "LangGraph integration requires optional dependencies. "
            "Install with: pip install nexus-fs-python[langgraph]"
        )
    get_nexus_tools = _langgraph_not_available  # type: ignore
    list_skills = _langgraph_not_available  # type: ignore

__all__ = [
    # Version
    "__version__",
    # Protocol
    "RPCErrorCode",
    "RPCRequest",
    "RPCResponse",
    "decode_rpc_message",
    "encode_rpc_message",
    # Exceptions
    "NexusError",
    "NexusFileNotFoundError",
    "NexusPermissionError",
    "PermissionDeniedError",
    "BackendError",
    "InvalidPathError",
    "MetadataError",
    "ValidationError",
    "ParserError",
    "ConflictError",
    "AuditLogError",
    "AuthenticationError",
    "RemoteFilesystemError",
    "RemoteConnectionError",
    "RemoteTimeoutError",
    "NotFoundError",
    # Clients
    "RemoteNexusFS",
    "RemoteMemory",
    "AsyncRemoteNexusFS",
    "AsyncRemoteMemory",
    # LangGraph (optional)
    "get_nexus_tools",
    "list_skills",
]

# Only export LangGraph functions if dependencies are available
if not _HAS_LANGGRAPH:
    __all__ = [item for item in __all__ if item not in ("get_nexus_tools", "list_skills")]
