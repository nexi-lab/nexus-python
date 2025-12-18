"""RPC protocol definitions for Nexus filesystem server.

This module defines the JSON-RPC protocol for exposing NexusFileSystem
operations over HTTP. Each method in the NexusFilesystem interface
maps to an RPC endpoint.

Protocol Format:
    POST /api/nfs/{method_name}

    Request:
    {
        "jsonrpc": "2.0",
        "id": "request-id",
        "params": {
            "arg1": value1,
            "arg2": value2
        }
    }

    Response (success):
    {
        "jsonrpc": "2.0",
        "id": "request-id",
        "result": {...}
    }

    Response (error):
    {
        "jsonrpc": "2.0",
        "id": "request-id",
        "error": {
            "code": -32000,
            "message": "Error message",
            "data": {...}
        }
    }
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any


class RPCErrorCode(Enum):
    """Standard JSON-RPC error codes + custom Nexus error codes."""

    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Nexus-specific errors
    FILE_NOT_FOUND = -32000
    FILE_EXISTS = -32001
    INVALID_PATH = -32002
    ACCESS_DENIED = -32003
    PERMISSION_ERROR = -32004
    VALIDATION_ERROR = -32005
    CONFLICT = -32006  # Optimistic concurrency conflict


@dataclass
class RPCRequest:
    """JSON-RPC request."""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str = ""
    params: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RPCRequest:
        """Create request from dict."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method", ""),
            params=data.get("params"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        result: dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.id is not None:
            result["id"] = self.id
        if self.params is not None:
            result["params"] = self.params
        return result


@dataclass
class RPCResponse:
    """JSON-RPC response."""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: Any = None
    error: dict[str, Any] | None = None

    @classmethod
    def success(cls, request_id: str | int | None, result: Any) -> RPCResponse:
        """Create success response."""
        return cls(id=request_id, result=result, error=None)

    @classmethod
    def create_error(
        cls,
        request_id: str | int | None,
        code: RPCErrorCode,
        message: str,
        data: Any = None,
    ) -> RPCResponse:
        """Create error response."""
        error_dict: dict[str, Any] = {"code": code.value, "message": message}
        if data is not None:
            error_dict["data"] = data
        return cls(id=request_id, result=None, error=error_dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        result: dict[str, Any] = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            result["id"] = self.id
        if self.error is not None:
            result["error"] = self.error
        else:
            result["result"] = self.result
        return result


class RPCEncoder(json.JSONEncoder):
    """Custom JSON encoder for RPC messages.

    Handles special types:
    - bytes: base64-encoded strings
    - datetime: ISO format strings
    - timedelta: total seconds
    """

    def default(self, obj: Any) -> Any:
        """Encode special types."""
        if isinstance(obj, bytes):
            return {"__type__": "bytes", "data": base64.b64encode(obj).decode("utf-8")}
        elif isinstance(obj, datetime):
            return {"__type__": "datetime", "data": obj.isoformat()}
        elif isinstance(obj, timedelta):
            return {"__type__": "timedelta", "seconds": obj.total_seconds()}
        elif isinstance(obj, date):
            return {"__type__": "datetime", "data": obj.isoformat()}
        elif hasattr(obj, "__dict__"):
            # Convert objects to dictionaries, filtering out methods
            return {
                k: v for k, v in obj.__dict__.items() if not k.startswith("_") and not callable(v)
            }
        return super().default(obj)


def rpc_decode_hook(obj: Any) -> Any:
    """Decode hook for special types."""
    if isinstance(obj, dict) and "__type__" in obj:
        if obj["__type__"] == "bytes":
            return base64.b64decode(obj["data"])
        elif obj["__type__"] == "datetime":
            return datetime.fromisoformat(obj["data"])
        elif obj["__type__"] == "timedelta":
            return timedelta(seconds=obj["seconds"])
    return obj


# Try to import orjson for faster JSON serialization (2-3x faster)
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def _prepare_for_orjson(obj: Any) -> Any:
    """Convert objects to orjson-compatible types for encoding responses.

    Handles all special types that RPCEncoder handles:
    - bytes: base64-encoded with __type__ wrapper
    - datetime/date: ISO format with __type__ wrapper
    - timedelta: seconds with __type__ wrapper
    - objects with __dict__: converted to dict
    """
    if isinstance(obj, bytes):
        return {"__type__": "bytes", "data": base64.b64encode(obj).decode("utf-8")}
    elif isinstance(obj, (datetime, date)):
        return {"__type__": "datetime", "data": obj.isoformat()}
    elif isinstance(obj, timedelta):
        return {"__type__": "timedelta", "seconds": obj.total_seconds()}
    elif isinstance(obj, dict):
        return {k: _prepare_for_orjson(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_prepare_for_orjson(item) for item in obj]
    elif hasattr(obj, "__dict__") and not isinstance(obj, type):
        return {
            k: _prepare_for_orjson(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
    else:
        return obj


def _apply_decode_hook(obj: Any) -> Any:
    """Recursively apply rpc_decode_hook to convert special types after orjson parsing.

    orjson doesn't support object_hook, so we apply it manually after parsing.
    """
    if isinstance(obj, dict):
        # First check if this dict is a special type wrapper
        if "__type__" in obj:
            return rpc_decode_hook(obj)
        # Otherwise recursively process all values
        return {k: _apply_decode_hook(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_apply_decode_hook(item) for item in obj]
    else:
        return obj


def encode_rpc_message(data: dict[str, Any]) -> bytes:
    """Encode RPC message to JSON bytes (uses orjson if available for 2-3x speedup)."""
    if HAS_ORJSON:
        # orjson is much faster and returns bytes directly
        # But it doesn't support custom encoders, so we ALWAYS pre-process the data
        # to ensure special types (bytes, datetime, timedelta) are wrapped with __type__
        prepared_data = _prepare_for_orjson(data)
        return orjson.dumps(prepared_data)
    else:
        # Fallback to standard json with custom encoder
        return json.dumps(data, cls=RPCEncoder).encode("utf-8")


def decode_rpc_message(data: bytes) -> dict[str, Any]:
    """Decode RPC message from JSON bytes (uses orjson if available).

    When orjson is used, we apply the decode hook manually after parsing
    to convert special types like {"__type__": "bytes", "data": "..."} back to bytes.
    """
    if HAS_ORJSON:
        parsed = orjson.loads(data)
        # Apply decode hook to convert special types (bytes, datetime, timedelta)
        return _apply_decode_hook(parsed)  # type: ignore[no-any-return]
    else:
        return json.loads(data.decode("utf-8"), object_hook=rpc_decode_hook)  # type: ignore[no-any-return]
