# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-01-10

### Added
- **Path Handling**: `read_file` tool now automatically handles unquoted paths with spaces
- **Tests**: Added comprehensive unit tests (20 test cases) for path parsing in `tests/test_read_file_path_parsing.py`

### Changed
- **read_file Tool**: Enhanced to intelligently detect and join path components containing spaces by scanning for line numbers
- **Documentation**: Improved `read_file` docstring with examples for paths with spaces

### Technical
- Smart path parser detects spaces in filenames by accumulating parts until finding valid line numbers
- Backward compatible: quoted paths continue to work as before
- Handles complex scenarios: long tenant paths, virtual parsed files (`*_parsed.{ext}.md`), line ranges

## [0.1.2] - 2026-01-08

### Added
- **Skills Discovery**: Added `skills_discover` method to `AsyncRemoteNexusFS` for listing available skills
- **Prompt Utilities**: New `nexus_client.langgraph.prompt` module with prompt generation utilities
  - `get_prompt_context()`: Generate LangGraph system prompts with Nexus context
  - `skills_discover()`: Retrieve skill metadata asynchronously

### Changed
- Updated LangGraph `__init__.py` to export new prompt utilities

## [0.1.1] - 2025-01-XX

### Changed
- **LangGraph Tools**: All LangGraph tool functions (`grep_files`, `glob_files`, `read_file`, `write_file`, `python`, `bash`, `query_memories`) are now fully asynchronous (`async def`)
- **Client Helper**: `_get_nexus_client()` now returns `AsyncRemoteNexusFS` and is async
- Improved compatibility with LangGraph Platform's async execution model

### Technical
- All Nexus filesystem operations in LangGraph tools now use `await` for proper async/await patterns
- Better performance and resource utilization in async LangGraph deployments

## [0.1.0] - 2025-12-18

### Added
- Initial release of nexus-client Python SDK
- Core remote filesystem client (`RemoteNexusFS`) with Python 3.11+ support
- Async client support (`AsyncRemoteNexusFS`)
- Remote Memory API client (`RemoteMemory`, `AsyncRemoteMemory`)
- LangGraph integration tools (optional dependency)
- Comprehensive test suite (51 tests)
- JSON-RPC 2.0 protocol implementation
- Retry logic with exponential backoff for transient failures
- Support for all core Nexus filesystem operations (read, write, list, grep, etc.)
- Skills API integration
- Semantic search support
- Workspace versioning support

### Features
- Lightweight package designed for LangGraph Platform deployments
- Backward compatible API with `nexus-ai-fs` remote client
- Optional LangGraph dependencies to keep core package minimal
- Comprehensive error handling with custom exception classes
- Connection pooling and timeout configuration
- Support for Python 3.11, 3.12, and 3.13

### Technical
- Built with `httpx` for HTTP client functionality
- Uses `tenacity` for retry logic
- Uses `pydantic` for data validation
- CI/CD pipeline with automated testing and PyPI publishing
- Full type hints support

