# Usage Examples

## Installation

```bash
# Core package (Python 3.11+)
pip install nexus-client

# With LangGraph support
pip install nexus-client[langgraph]
```

## Basic Usage

### Direct Client Usage

```python
from nexus_client import RemoteNexusFS

# Initialize client
nx = RemoteNexusFS("http://localhost:8080", api_key="sk-your-api-key")

# File operations
content = nx.read("/workspace/file.txt")
nx.write("/workspace/output.txt", b"Hello, World!")
files = nx.list("/workspace")

# File discovery
python_files = nx.glob("*.py", "/workspace")
results = nx.grep("def ", path="/workspace", file_pattern="*.py")

# Cleanup
nx.close()
```

### Async Client Usage

```python
import asyncio
from nexus_client import AsyncRemoteNexusFS

async def main():
    async with AsyncRemoteNexusFS("http://localhost:8080", api_key="sk-xxx") as nx:
        # Single operation
        content = await nx.read("/workspace/file.txt")
        await nx.write("/workspace/output.txt", b"Hello, World!")
        
        # Parallel operations (main benefit of async)
        paths = ["/file1.txt", "/file2.txt", "/file3.txt"]
        contents = await asyncio.gather(*[nx.read(p) for p in paths])
        
        print(f"Read {len(contents)} files in parallel")

asyncio.run(main())
```

## LangGraph Integration

### Basic Agent Setup

```python
from nexus_client.langgraph import get_nexus_tools
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Get Nexus tools
tools = get_nexus_tools()

# Create LLM
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

# Create agent
agent = create_react_agent(model=llm, tools=tools)

# Invoke with authentication
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find all Python files"}]},
    config={
        "metadata": {
            "x_auth": "Bearer sk-your-api-key",
            "nexus_server_url": "http://localhost:8080"
        }
    }
)
```

### Available Tools

The `get_nexus_tools()` function returns 7 LangGraph tools:

1. **grep_files** - Search file content
   ```python
   grep_files("async def", path="/workspace", file_pattern="*.py")
   ```

2. **glob_files** - Find files by pattern
   ```python
   glob_files("*.py", path="/workspace")
   ```

3. **read_file** - Read file content
   ```python
   read_file("cat /workspace/file.txt")
   read_file("less /workspace/large.py")  # Preview first 100 lines
   read_file("cat /workspace/file.txt 10 20")  # Lines 10-20
   ```

4. **write_file** - Write file content
   ```python
   write_file("/workspace/output.txt", "Hello, World!")
   ```

5. **python** - Execute Python code in sandbox
   ```python
   python("import pandas as pd\nprint(pd.DataFrame({'a': [1,2,3]}))")
   # Requires sandbox_id in metadata
   ```

6. **bash** - Execute bash commands
   ```python
   bash("ls -la /workspace")
   # Requires sandbox_id in metadata
   ```

7. **query_memories** - Query stored memories
   ```python
   query_memories()  # Returns all active memories
   ```

## Memory Operations

### Using Memory API

```python
from nexus_client import RemoteNexusFS

nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")

# Store memory
memory_id = nx.memory.store(
    content="User prefers dark mode",
    importance=0.8,
    namespace="user_preferences"
)

# Query memories
memories = nx.memory.query(
    query="user preferences",
    limit=10
)

# List all memories
all_memories = nx.memory.list(state="active", limit=50)

# Trajectory tracking
traj_id = nx.memory.start_trajectory("Process data", task_type="data_processing")
nx.memory.log_step(traj_id, "action", "Loaded 1000 records")
nx.memory.complete_trajectory(traj_id, "success", success_score=0.95)
```

## Sandbox Operations

### Creating and Using Sandboxes

```python
from nexus_client import RemoteNexusFS

nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")

# Create sandbox
sandbox = nx.sandbox_create(
    name="data-analysis",
    ttl_minutes=30,
    provider="e2b"
)
sandbox_id = sandbox["sandbox_id"]

# Run Python code
result = nx.sandbox_run(
    sandbox_id=sandbox_id,
    language="python",
    code="import pandas as pd\nprint(pd.__version__)",
    timeout=300
)
print(result["stdout"])

# Run bash command
result = nx.sandbox_run(
    sandbox_id=sandbox_id,
    language="bash",
    code="ls -la /workspace",
    timeout=300
)

# Check status
status = nx.sandbox_status(sandbox_id)
print(f"Sandbox status: {status['status']}")

# Stop sandbox
nx.sandbox_stop(sandbox_id)
```

## Skills Operations

### Listing and Using Skills

```python
from nexus_client import RemoteNexusFS

nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")

# List all skills
skills = nx.skills_list(tier="all", include_metadata=True)
print(f"Found {skills['count']} skills")

# Get skill info
skill_info = nx.skills_info("my-skill")
print(skill_info["description"])

# Search skills
results = nx.skills_search("data processing")
for skill in results:
    print(f"- {skill['name']}: {skill['description']}")
```

## Error Handling

### Handling Exceptions

```python
from nexus_client import (
    RemoteNexusFS,
    NexusFileNotFoundError,
    NexusPermissionError,
    RemoteConnectionError,
    ConflictError,
)

nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")

try:
    content = nx.read("/workspace/file.txt")
except NexusFileNotFoundError as e:
    print(f"File not found: {e.path}")
except NexusPermissionError as e:
    print(f"Permission denied: {e.path}")
except RemoteConnectionError as e:
    print(f"Connection failed: {e}")
except ConflictError as e:
    print(f"Conflict: expected {e.expected_etag}, got {e.current_etag}")
    # Retry with fresh read
    result = nx.read("/workspace/file.txt", return_metadata=True)
    nx.write("/workspace/file.txt", content, if_match=result["etag"])
```

## Environment Variables

### Configuration via Environment

```python
import os
from nexus_client import RemoteNexusFS

# Set environment variables
os.environ["NEXUS_URL"] = "http://localhost:8080"
os.environ["NEXUS_API_KEY"] = "sk-your-api-key"

# Client can auto-detect (if implemented)
# For now, pass explicitly:
nx = RemoteNexusFS(
    server_url=os.getenv("NEXUS_URL", "http://localhost:8080"),
    api_key=os.getenv("NEXUS_API_KEY")
)
```

## LangGraph Deployment Example

### Complete LangGraph Agent

```python
#!/usr/bin/env python3
"""Complete LangGraph agent with Nexus integration."""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langgraph.prebuilt import create_react_agent
from nexus_client.langgraph import get_nexus_tools

# Get tools
tools = get_nexus_tools()

# Create LLM
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", max_tokens=10000)

# Build dynamic prompt
def build_prompt(state: dict, config: RunnableConfig) -> list:
    """Build prompt with context."""
    system_content = "You are a helpful AI assistant with Nexus filesystem access."
    
    # Add opened file context if available
    metadata = config.get("metadata", {})
    opened_file = metadata.get("opened_file_path")
    if opened_file:
        system_content += f"\n\nCurrently viewing: {opened_file}"
    
    return [SystemMessage(content=system_content)] + state["messages"]

# Create agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=RunnableLambda(build_prompt),
)

# Use agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find all TODO comments"}]},
    config={
        "metadata": {
            "x_auth": "Bearer sk-your-api-key",
            "nexus_server_url": "http://localhost:8080"
        }
    }
)
```

## Best Practices

### 1. Connection Management

```python
# Use context manager for async
async with AsyncRemoteNexusFS("http://localhost:8080", api_key="sk-xxx") as nx:
    # Operations
    pass

# Explicitly close sync client
nx = RemoteNexusFS("http://localhost:8080", api_key="sk-xxx")
try:
    # Operations
    pass
finally:
    nx.close()
```

### 2. Error Handling

```python
# Always handle file not found
try:
    content = nx.read("/path/to/file.txt")
except NexusFileNotFoundError:
    # Create file or handle gracefully
    nx.write("/path/to/file.txt", b"default content")
```

### 3. Batch Operations

```python
# Use write_batch for multiple files (faster)
files = [
    ("/file1.txt", b"content1"),
    ("/file2.txt", b"content2"),
    ("/file3.txt", b"content3"),
]
results = nx.write_batch(files)
```

### 4. Parallel Async Operations

```python
# Read multiple files in parallel
paths = ["/file1.txt", "/file2.txt", "/file3.txt"]
contents = await asyncio.gather(*[nx.read(p) for p in paths])
```

## Migration from nexus-ai-fs

### Import Changes

```python
# Before
from nexus.remote import RemoteNexusFS
from nexus.tools.langgraph import get_nexus_tools

# After
from nexus_client import RemoteNexusFS
from nexus_client.langgraph import get_nexus_tools
```

### Configuration Changes

```toml
# Before (pyproject.toml)
requires-python = ">=3.13"
dependencies = ["nexus-ai-fs>=0.6.4"]

# After
requires-python = ">=3.11"
dependencies = ["nexus-client>=0.1.0"]
```

That's it! The API is identical, so no code changes needed beyond imports.
