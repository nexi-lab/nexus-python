# API Reference

This document provides a reference for the Nexus Python Client SDK APIs.

## Core File Operations

### 1. Read File
```python
content = nx.read(path: str, return_metadata: bool = False) -> bytes | dict
```
- Used by: `read_file` tool
- Returns: File content as bytes, or dict with metadata if `return_metadata=True`

### 2. Write File
```python
result = nx.write(path: str, content: bytes, if_match: str | None = None) -> dict
```
- Used by: `write_file` tool
- Returns: Dict with `etag`, `version`, `modified_at`, `size`

### 3. Delete File
```python
nx.delete(path: str) -> None
```
- Used by: File management operations

### 4. Check Existence
```python
exists = nx.exists(path: str) -> bool
```
- Used by: `write_file` tool (verification)

## File Discovery Operations

### 5. List Files
```python
files = nx.list(path: str = "/", recursive: bool = True, details: bool = False) -> list[str] | list[dict]
```
- Used by: Directory browsing operations

### 6. Glob Pattern Search
```python
matches = nx.glob(pattern: str, path: str = "/") -> list[str]
```
- Used by: `glob_files` tool
- Example: `nx.glob("*.py", "/workspace")` → `["/workspace/file1.py", "/workspace/file2.py"]`

### 7. Grep Content Search
```python
results = nx.grep(
    pattern: str,
    path: str = "/",
    file_pattern: str | None = None,
    ignore_case: bool = False,
    max_results: int = 1000
) -> list[dict]
```
- Used by: `grep_files` tool
- Returns: List of dicts with `file`, `line`, `content`, `match`
- Example: `nx.grep("async def", path="/workspace", file_pattern="*.py")`

## Sandbox Operations

### 8. Create Sandbox
```python
sandbox = nx.sandbox_create(provider: str = "docker", config: dict | None = None) -> dict
```
- Returns: Dict with `sandbox_id`, `status`, etc.

### 9. Run Code in Sandbox
```python
result = nx.sandbox_run(
    sandbox_id: str,
    language: str,  # "python" or "bash"
    code: str,
    timeout: int = 300
) -> dict
```
- Used by: `python` and `bash` tools
- Returns: Dict with `stdout`, `stderr`, `exit_code`, `execution_time`

### 10. Sandbox Lifecycle
```python
nx.sandbox_pause(sandbox_id: str) -> dict
nx.sandbox_resume(sandbox_id: str) -> dict
nx.sandbox_stop(sandbox_id: str) -> dict
nx.sandbox_status(sandbox_id: str) -> dict
nx.sandbox_list() -> list[dict]
```

## Memory Operations

### 11. Store Memory
```python
memory_id = nx.memory.store(
    content: str,
    namespace: str | None = None,
    importance: float | None = None
) -> str
```
- Stores agent memory/context

### 12. Query Memories
```python
memories = nx.memory.query(
    query: str,
    namespace: str | None = None,
    limit: int = 10
) -> list[dict]
```
- Used by: `query_memories` tool
- Returns: List of memory dicts with `content`, `namespace`, `importance`, etc.

### 13. List Memories
```python
memories = nx.memory.list(
    scope: str | None = None,
    state: str = "active",
    limit: int = 50
) -> list[dict]
```
- Used by: `query_memories` tool (when no query provided)

### 14. Retrieve Memory
```python
memory = nx.memory.retrieve(
    namespace: str | None = None,
    path_key: str | None = None
) -> dict | None
```

### 15. Delete Memory
```python
success = nx.memory.delete(memory_id: str) -> bool
```

## Skills Operations

### 16. List Skills
```python
skills = nx.skills_list(tier: str | None = None, include_metadata: bool = True) -> dict
```
- Used by: `list_skills()` function
- Returns: Dict with `skills` (list) and `count`
- Tiers: `"all"`, `"agent"`, `"user"`, `"tenant"`, `"system"`

### 17. Get Skill Info
```python
skill = nx.skills_info(skill_name: str) -> dict
```

### 18. Search Skills
```python
results = nx.skills_search(query: str) -> list[dict]
```

## RPC Protocol

### Internal RPC Method
```python
result = nx._call_rpc(method: str, params: dict | None = None) -> Any
```
- Internal method for making RPC calls
- Handles retries, error handling, authentication
- All public methods use this internally

## Authentication

### Client Initialization
```python
nx = RemoteNexusFS(
    server_url: str,  # e.g., "http://localhost:8080"
    api_key: str,      # e.g., "sk-xxx"
    timeout: int = 90,
    max_retries: int = 3
)
```

### From LangGraph Config
```python
# Extracts from config.metadata:
# - x_auth: "Bearer sk-xxx" → api_key
# - nexus_server_url: "http://localhost:8080" → server_url

nx = _get_nexus_client(config: RunnableConfig, state: dict | None = None) -> RemoteNexusFS
```

## LangGraph Tools API

### Tool Creation
```python
tools = get_nexus_tools() -> list[BaseTool]
```

### Individual Tools

1. **grep_files(pattern, path="/", file_pattern=None, ignore_case=False, max_results=1000)**
   - Calls: `nx.grep()`
   - Returns: Formatted grep-style output

2. **glob_files(pattern, path="/")**
   - Calls: `nx.glob()`
   - Returns: Formatted file list

3. **read_file(read_cmd: str)**
   - Parses: `"cat path"`, `"less path"`, `"cat path start end"`
   - Calls: `nx.read()`
   - Returns: Formatted file content

4. **write_file(path: str, content: str)**
   - Calls: `nx.write()`
   - Verifies: `nx.exists()`
   - Returns: Success message

5. **python(code: str)**
   - Requires: `sandbox_id` in `config.metadata`
   - Calls: `nx.sandbox_run(sandbox_id, language="python", code=code)`
   - Returns: Formatted stdout/stderr

6. **bash(command: str)**
   - Requires: `sandbox_id` in `config.metadata`
   - Calls: `nx.sandbox_run(sandbox_id, language="bash", code=command)`
   - Returns: Formatted stdout/stderr

7. **query_memories()**
   - Calls: `nx.memory.query(state="active", limit=100)`
   - Returns: Formatted memory list

## Error Handling

### Exception Hierarchy
```
NexusError (base)
├── NexusFileNotFoundError
├── InvalidPathError
├── NexusPermissionError
├── ValidationError
├── ConflictError
└── RemoteFilesystemError
    ├── RemoteConnectionError
    └── RemoteTimeoutError
```

## Usage Example

```python
from nexus_client import RemoteNexusFS
from nexus_client.langgraph import get_nexus_tools

# Direct usage
nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")
content = nx.read("/workspace/file.txt")
nx.write("/workspace/output.txt", b"Hello, World!")
files = nx.glob("*.py", "/workspace")

# LangGraph usage
tools = get_nexus_tools()
agent = create_react_agent(model=llm, tools=tools)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find Python files"}]},
    config={"metadata": {"x_auth": "Bearer sk-xxx", "nexus_server_url": "http://localhost:8080"}}
)
```

## Priority APIs for MVP

**Must Have (Core Functionality)**:
1. ✅ read, write, delete, exists
2. ✅ list, glob, grep
3. ✅ memory.store, memory.query, memory.list
4. ✅ sandbox_run (for python/bash tools)

**Should Have (Full Feature Set)**:
5. ✅ skills_list, skills_info
6. ✅ sandbox_create, sandbox_status, sandbox_list
7. ✅ stat, read_range, write_batch

**Nice to Have (Advanced Features)**:
8. ⚠️ Advanced memory operations (retrieve, delete)
9. ⚠️ Advanced sandbox operations (pause, resume, stop)
10. ⚠️ Skills operations (create, search)
