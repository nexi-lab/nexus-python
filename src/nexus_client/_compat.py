"""Compatibility stubs for nexus-ai-fs base classes.

This module provides minimal stubs for base classes that RemoteNexusFS
inherits from in nexus-ai-fs, ensuring API compatibility without requiring
the full nexus-ai-fs package.
"""

from abc import ABC, abstractmethod


class NexusFilesystem(ABC):
    """Abstract base class for Nexus filesystem implementations.

    This is a minimal stub for compatibility. RemoteNexusFS implements
    all required methods from this interface.
    """

    @property
    @abstractmethod
    def agent_id(self) -> str | None:
        """Agent ID for this filesystem instance."""
        ...

    @property
    @abstractmethod
    def tenant_id(self) -> str | None:
        """Tenant ID for this filesystem instance."""
        ...


class NexusFSLLMMixin:
    """Mixin for LLM-powered document reading capabilities.

    This is a minimal stub for compatibility. RemoteNexusFS includes
    LLM methods via this mixin, but they require additional dependencies
    that are not included in the base nexus-client package.

    For full LLM functionality, use nexus-ai-fs or install additional
    dependencies.
    """

    # LLM methods are implemented in RemoteNexusFS but may require
    # additional dependencies (llm providers, etc.)
    pass
