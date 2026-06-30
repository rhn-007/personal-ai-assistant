from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Base class for every tool."""

    name = "base"

    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Return True if this tool should handle the query."""
        pass

    @abstractmethod
    def execute(self, query: str):
        """Execute the tool."""
        pass
