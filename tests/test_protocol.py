"""Tests for RPC protocol encoding/decoding."""

from datetime import datetime, timedelta

from nexus_client.protocol import (
    RPCErrorCode,
    RPCRequest,
    RPCResponse,
    decode_rpc_message,
    encode_rpc_message,
)


def test_rpc_request_to_dict():
    """Test RPCRequest serialization."""
    request = RPCRequest(method="read", params={"path": "/test.txt"}, id="123")
    data = request.to_dict()
    assert data["jsonrpc"] == "2.0"
    assert data["method"] == "read"
    assert data["id"] == "123"
    assert data["params"] == {"path": "/test.txt"}


def test_rpc_request_from_dict():
    """Test RPCRequest deserialization."""
    data = {"jsonrpc": "2.0", "method": "read", "id": "123", "params": {"path": "/test.txt"}}
    request = RPCRequest.from_dict(data)
    assert request.method == "read"
    assert request.id == "123"
    assert request.params == {"path": "/test.txt"}


def test_rpc_response_success():
    """Test RPCResponse success creation."""
    response = RPCResponse.success("123", {"content": "test"})
    data = response.to_dict()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == "123"
    assert data["result"] == {"content": "test"}
    assert "error" not in data


def test_rpc_response_error():
    """Test RPCResponse error creation."""
    response = RPCResponse.create_error("123", RPCErrorCode.FILE_NOT_FOUND, "File not found")
    data = response.to_dict()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == "123"
    assert data["error"]["code"] == -32000
    assert data["error"]["message"] == "File not found"
    assert "result" not in data


def test_encode_decode_bytes():
    """Test encoding/decoding of bytes."""
    data = {"content": b"Hello, World!"}
    encoded = encode_rpc_message(data)
    decoded = decode_rpc_message(encoded)
    assert decoded["content"] == b"Hello, World!"


def test_encode_decode_datetime():
    """Test encoding/decoding of datetime."""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    data = {"timestamp": dt}
    encoded = encode_rpc_message(data)
    decoded = decode_rpc_message(encoded)
    assert isinstance(decoded["timestamp"], datetime)
    assert decoded["timestamp"] == dt


def test_encode_decode_timedelta():
    """Test encoding/decoding of timedelta."""
    td = timedelta(hours=2, minutes=30)
    data = {"duration": td}
    encoded = encode_rpc_message(data)
    decoded = decode_rpc_message(encoded)
    assert isinstance(decoded["duration"], timedelta)
    assert decoded["duration"] == td


def test_encode_decode_complex():
    """Test encoding/decoding of complex nested structures."""
    data = {
        "file": {
            "path": "/test.txt",
            "content": b"Binary content",
            "created": datetime(2024, 1, 1),
            "duration": timedelta(hours=1),
        }
    }
    encoded = encode_rpc_message(data)
    decoded = decode_rpc_message(encoded)
    assert decoded["file"]["path"] == "/test.txt"
    assert decoded["file"]["content"] == b"Binary content"
    assert isinstance(decoded["file"]["created"], datetime)
    assert isinstance(decoded["file"]["duration"], timedelta)
