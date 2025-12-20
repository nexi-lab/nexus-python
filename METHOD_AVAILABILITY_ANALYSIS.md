# RPC Method Availability Analysis

## Summary

Testing against `https://nexus-server.multifi.ai` revealed that **2 methods are not available** on this server:

1. **`stat()`** - File metadata method
2. **`query_memories()` / `list_memories()`** - Memory query methods

## Detailed Findings

### 1. `stat()` Method - ❌ Not Available

**Client Implementation:**
- Location: `src/nexus_client/client.py:1050`
- RPC Call: `_call_rpc("stat", {"path": path})`
- Purpose: Get file metadata (size, etag, version, modified_at, is_directory) without reading content

**Server Response:**
```
RPC error [-32602]: Invalid parameters: Unknown method: stat
```

**Impact:**
- The `stat()` method is used by `stream()` method to get file size before streaming
- Without `stat()`, we cannot efficiently get file metadata without reading the file

**Alternatives Available:**
1. ✅ **`get_metadata()`** - Available but returns `None` for test file (may need different path or permissions)
   - Location: `src/nexus_client/client.py:1547`
   - RPC Call: `_call_rpc("get_metadata", {"path": path})`
   - Returns: Metadata dict with `path`, `owner`, `group`, `mode`, `is_directory`
   - **Note:** This is different from `stat()` - it's for FUSE operations (permissions/ownership), not file size/etag

2. ✅ **`list()` with `details=True`** - Can get file metadata as part of directory listing
   - Location: `src/nexus_client/client.py:1368`
   - Returns: List of dicts with file metadata when `details=True`

3. ⚠️ **`get_etag()`** - Depends on server implementation
   - Location: `src/nexus_client/client.py:1348`
   - RPC Call: `_call_rpc("get_etag", {"path": path})`
   - **Note:** Currently fails because it expects a result dict, but server may not support it

**Workarounds:**
```python
# Instead of:
stat_info = nx.stat(path)
file_size = stat_info['size']

# Use:
# Option 1: Read file to get size (inefficient for large files)
content = nx.read(path)
file_size = len(content)

# Option 2: Use list() with details=True
files = nx.list(os.path.dirname(path), details=True)
file_info = next((f for f in files if f['path'] == path), None)
if file_info:
    file_size = file_info.get('size')
```

### 2. Memory API Methods - ❌ Not Available

**Client Implementation:**
- `memory.list()` → `_call_rpc("list_memories", params)`
- `memory.query()` → `_call_rpc("query_memories", params)`
- `memory.search()` → `_call_rpc("query_memories", params)` (with query parameter)

**Server Response:**
```
RPC error [-32602]: Invalid parameters: Unknown method: list_memories
RPC error [-32602]: Invalid parameters: Unknown method: query_memories
```

**Impact:**
- All memory query operations fail
- Memory storage (`memory.store()`) may still work (not tested)
- LangGraph `query_memories` tool will not work

**Possible Reasons:**
1. **Server Version Mismatch**: The server may be running an older version that doesn't have memory API endpoints
2. **Feature Flag**: Memory API might be disabled on this server instance
3. **Different Method Names**: The server might use different RPC method names

**What Works:**
- ✅ File operations (read, write, list, glob, grep)
- ✅ Skills API (`skills_list()`)
- ✅ Basic filesystem operations

**What Doesn't Work:**
- ❌ Memory API queries
- ❌ File metadata via `stat()`
- ⚠️ File metadata via `get_metadata()` (returns None, may need investigation)

## Root Cause Analysis

### Server Version Compatibility

The client SDK was extracted from `nexus-ai-fs` which targets newer server versions. The server at `nexus-server.multifi.ai` appears to be running an **older version** that doesn't implement:

1. **`stat` RPC endpoint** - This is a newer feature for efficient metadata retrieval
2. **Memory API RPC endpoints** - `list_memories` and `query_memories` may not be exposed

### Client Design

The client is designed to be **backward compatible** with the `nexus-ai-fs` API, but it assumes the server has all the same RPC endpoints. When methods are missing, the client correctly:

1. ✅ Makes the RPC call
2. ✅ Receives the "Unknown method" error
3. ✅ Raises a `RemoteFilesystemError` with clear error message
4. ✅ Allows the application to handle the error gracefully

## Recommendations

### For Application Developers

1. **Handle Missing Methods Gracefully:**
   ```python
   try:
       stat_info = nx.stat(path)
       file_size = stat_info['size']
   except RemoteFilesystemError as e:
       if "Unknown method" in str(e):
           # Fallback: read file to get size
           content = nx.read(path)
           file_size = len(content)
       else:
           raise
   ```

2. **Check Method Availability:**
   ```python
   def has_stat_method(nx: RemoteNexusFS) -> bool:
       try:
           nx.stat("/")  # Try root path
           return True
       except RemoteFilesystemError as e:
           return "Unknown method" not in str(e)
   ```

3. **Use Alternative Methods:**
   - For file size: Use `list()` with `details=True` or read the file
   - For memory: Check if memory API is available before using it

### For Server Administrators

1. **Upgrade Server**: Update to a version that supports `stat` and memory API endpoints
2. **Check Server Logs**: Verify which RPC methods are registered
3. **Feature Flags**: Ensure memory API is enabled if using that feature

### For Client SDK Maintainers

1. **Add Method Detection**: Consider adding a `check_method_availability()` helper
2. **Document Server Requirements**: Clearly document which server versions support which methods
3. **Graceful Degradation**: Consider adding fallback implementations for missing methods

## Testing Results

```
✅ Available:
   - get_metadata() (returns None for test file, may need investigation)
   - File operations (read, write, list, glob, grep)
   - Skills API

❌ Not Available:
   - stat()
   - list_memories()
   - query_memories()
   - get_etag() (fails due to None result from get_metadata)
```

## Conclusion

The skipped tests are **expected behavior** - the server simply doesn't implement these methods. The client SDK correctly handles this by:

1. Making the RPC call
2. Receiving the "Unknown method" error
3. Raising an appropriate exception
4. Allowing the application to handle it

This is **not a bug** in the client SDK, but rather a **server version compatibility issue**. The client is working as designed - it exposes the full API surface, and gracefully handles cases where the server doesn't support certain methods.

