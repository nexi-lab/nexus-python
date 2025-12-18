# Nexus Python Client SDK

> Lightweight Python 3.11+ client SDK for Nexus filesystem, designed for LangGraph deployments

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## Overview

A standalone Python client SDK for Nexus that enables LangGraph agents to interact with Nexus servers. This package is designed for Python 3.11+ compatibility, making it suitable for LangGraph Platform deployments (which support Python 3.11 and 3.12).

**Key Features:**
- ✅ Python 3.11+ compatible (works with LangGraph Platform)
- ✅ Lightweight - Minimal dependencies, fast installation
- ✅ Complete API - All APIs needed by LangGraph agents
- ✅ LangGraph Ready - Pre-built tool adaptors included
- ✅ 100% API compatible with `nexus-ai-fs` remote client

## Installation

```bash
# Core package
pip install nexus-fs-python

# With LangGraph support
pip install nexus-fs-python[langgraph]
```

## Quick Start

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

### LangGraph Integration

```python
from nexus_client.langgraph import get_nexus_tools
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Get Nexus tools
tools = get_nexus_tools()

# Create agent
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
agent = create_react_agent(model=llm, tools=tools)

# Use agent
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

### Async Usage

```python
import asyncio
from nexus_client import AsyncRemoteNexusFS

async def main():
    async with AsyncRemoteNexusFS("http://localhost:8080", api_key="sk-xxx") as nx:
        # Parallel operations
        paths = ["/file1.txt", "/file2.txt", "/file3.txt"]
        contents = await asyncio.gather(*[nx.read(p) for p in paths])

asyncio.run(main())
```

## LangGraph Tools

The SDK provides 7 ready-to-use LangGraph tools:

1. **`grep_files`** - Search file content with regex patterns
2. **`glob_files`** - Find files by glob pattern
3. **`read_file`** - Read file content (supports cat/less style commands)
4. **`write_file`** - Write content to filesystem
5. **`python`** - Execute Python code in Nexus-managed sandbox
6. **`bash`** - Execute bash commands in sandbox
7. **`query_memories`** - Query and retrieve stored memory records

## Core APIs

### File Operations
- `read()`, `write()`, `delete()`, `exists()`, `stat()`
- `list()`, `glob()`, `grep()`
- `mkdir()`, `rename()`

### Sandbox Operations
- `sandbox_create()`, `sandbox_run()`, `sandbox_status()`
- `sandbox_pause()`, `sandbox_resume()`, `sandbox_stop()`

### Memory Operations
- `memory.store()`, `memory.query()`, `memory.list()`
- `memory.retrieve()`, `memory.delete()`
- `memory.start_trajectory()`, `memory.log_step()`, `memory.complete_trajectory()`

### Skills Operations
- `skills_list()`, `skills_info()`, `skills_search()`

## Dependencies

### Core (Required)
- `httpx>=0.27.0` - HTTP client
- `tenacity>=8.0.0` - Retry logic
- `pydantic>=2.0.0` - Data validation

### Optional: LangGraph
```bash
pip install nexus-client[langgraph]
```
- `langchain-core>=0.3.0`
- `langgraph>=0.2.0`

## API Compatibility

This package maintains **100% API compatibility** with `nexus-ai-fs` remote client. Migration is simple:

```python
# Before (nexus-ai-fs)
from nexus.remote import RemoteNexusFS
from nexus.tools.langgraph import get_nexus_tools

# After (nexus-client)
from nexus_client import RemoteNexusFS
from nexus_client.langgraph import get_nexus_tools
```

No code changes needed beyond imports!

## Documentation

- **[Usage Examples](./USAGE_EXAMPLES.md)** - Comprehensive usage guide with code examples
- **[API Reference](./API_SUMMARY.md)** - Complete API documentation

## Requirements

- Python 3.11, 3.12, or 3.13
- Nexus server (remote or local)

## License

Apache 2.0 - see [LICENSE](./LICENSE) for details.

## Contributing

Contributions welcome! Please see the main [Nexus repository](https://github.com/nexi-lab/nexus) for contribution guidelines.

## Related

- [Nexus Repository](https://github.com/nexi-lab/nexus) - Main Nexus filesystem
- [GitHub Issue #661](https://github.com/nexi-lab/nexus/issues/661) - Original feature request
