# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of Nexus Python Client SDK
- Python 3.11+ compatibility for LangGraph Platform deployments
- Complete remote filesystem client (`RemoteNexusFS`)
- Async filesystem client (`AsyncRemoteNexusFS`)
- Memory API client (`RemoteMemory`, `AsyncRemoteMemory`)
- LangGraph integration with 7 ready-to-use tools
- Comprehensive test suite
- Full API compatibility with `nexus-ai-fs` remote client

### Features
- File operations: read, write, delete, list, glob, grep
- Sandbox operations: create, run, pause, resume, stop
- Memory operations: store, query, list, retrieve, delete
- Skills operations: list, info, search
- RPC protocol with automatic retry and error handling
- Optional LangGraph dependencies for lightweight core package
